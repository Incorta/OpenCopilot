import logo from './logo.svg';
import ChatWindow from 'pages/ChatWindow.js';
import { SessionProvider } from 'contexts/SessionProvider.js';
import './App.css';

function App() {
  return (
    <div className="App">
      <SessionProvider>
        <ChatWindow />
      </SessionProvider>
    </div>
  );
}

export default App;
