import React from 'react';
import Game from './components/Game';
import './styles/game.css'

export default class App extends React.Component {

    render() {
        return (
            <div
                style={{
                    fontFamily: 'sans-serif',
                    textAlign: 'center',
                    // width: '100vw',
                    // height: '100vh',
                    overflow: 'hidden'
                }}
            >
                <h1>Yay!</h1>
                <Game />
            </div>
        );
    }

}
