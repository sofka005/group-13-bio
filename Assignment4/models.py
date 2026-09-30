"""Pre-implemented models of sound event recognition."""

import torch

from config import N_MELS, SAMPLE_RATE, SNIPPET_DURATION


class WaveformModel(torch.nn.Module):
    """ Super simple model that operates directly on raw waveforms: 5 fully connected layers with tanh activations,
    followed by a linear classifier returning logits.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        input_length = int(SAMPLE_RATE * SNIPPET_DURATION)
        hidden_sizes = (1024, 512, 256, 128, 64)

        self.flatten = torch.nn.Flatten()

        sizes = [input_length, *hidden_sizes]
        self.hidden_layers = torch.nn.ModuleList([
            torch.nn.Linear(sizes[i], sizes[i + 1]) for i in range(len(hidden_sizes))
        ])
        self.activation = torch.nn.Tanh()

        self.classifier = torch.nn.Linear(hidden_sizes[-1], num_classes)

    def forward(
            self,
            waveform: torch.Tensor
    ) -> torch.Tensor:
        x = self.flatten(waveform)
        for layer in self.hidden_layers:
            x = self.activation(layer(x))
        return self.classifier(x)


class UninspiredModel(torch.nn.Module):
    """ More complex but still uninspired model that now operates on spectrograms: 3 convolutional layers with
    tanh activations, followed by 2 fully connected layers and a linear classifier returning logits.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        conv_channels = (1, 16, 32, 64)
        fc_sizes = (64, 128, 64)

        self.conv_layers = torch.nn.ModuleList([
            torch.nn.Conv2d(conv_channels[i], conv_channels[i + 1], kernel_size=3, padding=1)
            for i in range(len(conv_channels) - 1)
        ])
        self.pool = torch.nn.MaxPool2d(2)
        self.activation = torch.nn.Tanh()

        self.fc_layers = torch.nn.ModuleList([
            torch.nn.Linear(fc_sizes[i], fc_sizes[i + 1]) for i in range(len(fc_sizes) - 1)
        ])

        self.classifier = torch.nn.Linear(fc_sizes[-1], num_classes)

    def forward(
            self,
            spectrogram: torch.Tensor
    ) -> torch.Tensor:
        x = spectrogram
        for conv in self.conv_layers:
            x = self.pool(self.activation(conv(x)))
        x = x.mean(dim=(-2, -1))
        for fc in self.fc_layers:
            x = self.activation(fc(x))
        return self.classifier(x)


class InspiredModel(torch.nn.Module):
    """ The most complex model, operating on spectrograms: 3 convolutional layers with ReLU6 activations extract local
    time-frequency features, 2 stacked recurrent (GRU) layers integrate information over time, and a linear classifier
    returns logits. Its conv -> recurrent structure loosely mirrors the auditory system's hierarchy of local
    spectrotemporal filtering followed by temporal integration.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        conv_channels = (1, 16, 32, 64)
        rnn_hidden_size = 128

        self.conv_layers = torch.nn.ModuleList([
            torch.nn.Conv2d(conv_channels[i], conv_channels[i + 1], kernel_size=3, padding=1)
            for i in range(len(conv_channels) - 1)
        ])
        self.pool = torch.nn.MaxPool2d(2)
        self.activation = torch.nn.ReLU6()

        self.rnn = torch.nn.GRU(
            input_size=conv_channels[-1], hidden_size=rnn_hidden_size, num_layers=2, batch_first=True,
        )

        self.classifier = torch.nn.Linear(rnn_hidden_size, num_classes)

    def forward(
            self,
            spectrogram: torch.Tensor
    ) -> torch.Tensor:
        """ Runs the model forward.

        Args:
            spectrogram: Tensor of shape (batch, 1, n_freq, n_time).

        Returns:
            Logits of shape (batch, num_classes).
        """
        x = spectrogram
        for conv in self.conv_layers:
            x = self.pool(self.activation(conv(x)))

        x = x.mean(dim=2).transpose(1, 2)

        _, hidden = self.rnn(x)
        last_hidden = hidden[-1]

        return self.classifier(last_hidden)


class AuditoryPathwayModel(torch.nn.Module):
    """ Part II: a CRNN whose stages loosely follow the ascending auditory pathway. Every stage's output passes
    through ReLU6 (non-negative, saturating firing rates); the recurrence inside `stg` uses a plain ReLU.

    Spectrogram frames are 25 ms apart (hop 200 samples at 8 kHz, 50 ms window).

    * `ic` (inferior colliculus) and `mgb` (medial geniculate body, thalamus): conv layers that keep full temporal
      resolution (1 frame = 25 ms) and pool only along frequency, i.e. fine timing as in the subcortical nuclei,
      while the frequency axis is progressively coarsened but kept as an ordered (tonotopic) map.
    * `a1` (primary auditory cortex, core): a spectrotemporal conv layer whose 5-frame kernel spans ~150 ms (more with
      the ic/mgb receptive fields stacked), followed by pooling in time too, mirroring the slower integration of cortex.
    * `belt` (belt / parabelt): a fully connected projection per time frame that reads out the *whole* tonotopic map
      (frequency is flattened rather than averaged away as in InspiredModel). A thalamocortical shortcut feeds the
      MGB output into the belt as well, since the MGB projects to both core and belt areas.
    * `stg` (superior temporal gyrus): a recurrent ReLU layer integrating the belt input over time.
    * `classifier`: linear readout from the time-averaged STG state.

    Args:
        num_classes: Number of output classes.
    """

    def __init__(
            self,
            num_classes: int
    ):
        super().__init__()
        channels = (1, 16, 32, 64)
        hidden_size = 128

        self.ic = torch.nn.Conv2d(channels[0], channels[1], kernel_size=(5, 3), padding=(2, 1))
        self.mgb = torch.nn.Conv2d(channels[1], channels[2], kernel_size=(3, 3), padding=1)
        self.a1 = torch.nn.Conv2d(channels[2], channels[3], kernel_size=(3, 5), padding=(1, 2))
        self.freq_pool = torch.nn.MaxPool2d((2, 1))
        self.spectrotemporal_pool = torch.nn.MaxPool2d(2)
        self.activation = torch.nn.ReLU6()
        self.dropout = torch.nn.Dropout(0.3)

        a1_features = channels[3] * (N_MELS // 8)
        mgb_features = channels[2] * (N_MELS // 4)
        self.belt = torch.nn.Linear(a1_features + mgb_features, hidden_size)
        self.stg = torch.nn.RNN(hidden_size, hidden_size, nonlinearity="relu", batch_first=True)

        self.classifier = torch.nn.Linear(hidden_size, num_classes)

    def forward(
            self,
            spectrogram: torch.Tensor
    ) -> torch.Tensor:
        """ Runs the model forward.

        Args:
            spectrogram: Tensor of shape (batch, 1, n_freq, n_time).

        Returns:
            Logits of shape (batch, num_classes).
        """
        x = spectrogram
        x = self.freq_pool(self.activation(self.ic(x)))
        mgb = self.freq_pool(self.activation(self.mgb(x)))            # (B, 32, F/4, T)
        a1 = self.spectrotemporal_pool(self.activation(self.a1(mgb)))  # (B, 64, F/8, T/2)

        # align the thalamic shortcut with A1's time resolution, then flatten channels x frequency per time frame
        mgb = torch.nn.functional.avg_pool2d(mgb, kernel_size=(1, 2))[..., :a1.shape[-1]]
        a1 = a1.flatten(1, 2).transpose(1, 2)    # (B, T/2, 64 * F/8)
        mgb = mgb.flatten(1, 2).transpose(1, 2)  # (B, T/2, 32 * F/4)

        belt = self.activation(self.belt(self.dropout(torch.cat([a1, mgb], dim=-1))))
        stg, _ = self.stg(belt)
        stg = self.activation(stg).mean(dim=1)

        return self.classifier(self.dropout(stg))
