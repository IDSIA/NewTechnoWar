import React from 'react'
import { BrowserRouter as Router, Switch, Route } from "react-router-dom"

import Game from './components/Game'
import Config from './components/Config'

export default class App extends React.Component {

    render() {
        return (
            <Router>
                <Switch>
                    <Route path="/config">
                        <Config />
                    </Route>
                    <Route path="/">
                        <Game />
                    </Route>
                </Switch>
            </Router>
        );
    }

}