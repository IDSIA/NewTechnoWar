# New Techno War

<img src="docs/ntw.jpg" alt="Crema" width="128"/>


**New Techno War** is tabletop [wargame](https://deftech.ch/it/wargaming/) developed by [Helvetia Games](https://helvetia-games.ch/) in collaboration with [Armasuisse](https://www.ar.admin.ch/en/armasuisse-wissenschaft-und-technologie-w-t/home.html). **New Techno War** makes it easy to simulate future systems integrating new technologies while stimulating discussions. The goal here is not to win, but to understand the strengths and weaknesses induced by these future systems in given tactical scenarios.

In this collaboration between IDSIA and Armasuisse, we aim to build a *companion agent* based on XAI that can help the players make strategical decisions and solving various combat scenario with different goals and constraints.


## Structure

This repository is structured in three parts:

* `code` contains all the [Python](https://www.python.org/) code necessary to play the game, develop agents or run experiments;
* `frontend` contains a WebApp build with [ReactJS](https://reactjs.org/) that can be used by humans to play the game in a web browser; and
* `docs` contains various kind of documentation.


## Demo version

In order to run a demo version, which is the game with the WebApp as frontend, use the following standard [Docker Compose](https://docs.docker.com/compose/) commands:

```bash
docker-compose build
docker-compose up -d
```

The WebApp will be reachable at the port `:8080`.


## More details

For more details on how to use this repository, please check the [Wiki](https://github.com/IDSIA/NewTechnoWar/wiki) for all the details.

