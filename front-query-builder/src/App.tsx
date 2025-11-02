import './App.css';
import { Header } from './components/Header';
import { QueryBuilder } from './components/QueryBuilder';
import { Visualization } from './components/Visualization';

function App() {
  return (
    <div className="app-layout">
      <Header />
      <QueryBuilder />
      <Visualization />
    </div>
  );
}

export default App;
