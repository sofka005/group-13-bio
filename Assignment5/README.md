## 1. Infection model run for 2 hours

Infection simulation in 30 minutes intervals (t denotes time from beginning of simulation in minutes)
<table>
  <tr>
    <td><img src="./img/t0.png" width="200"/><br/><sub>t = 0</sub></td>
    <td><img src="./img/t30.png" width="200"/><br/><sub>t = 30</sub></td>
    <td><img src="./img/t60.png" width="200"/><br/><sub>t = 60</sub></td>
    <td><img src="./img/t90.png" width="200"/><br/><sub>t = 90</sub></td>
    <td><img src="./img/t120.png" width="200"/><br/><sub>t = 120</sub></td>
  </tr>
</table>

As the pathogen releases chemicals that weaken the cell walls, it starts pushing them in and growing in size. If we run the simulation for a longer time, the pathogen actually starts cell division to multiply inside the plant. The plant cells deform relative to their original shape, because the growing pathogen pushes them. The pathogen can also destroy a plant's cell wall once it weakens it enough. We can see, for example, that in the start of the simulation there is a wall separating the two cells that the pathogen is nested between, but as it grows it destroys the wall and is the only separator between them. 