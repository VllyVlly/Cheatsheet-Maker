import FileUpload from "./FileUpload";
import './App.css'

function App() {
  return (
    <div className="App">
      <div className="title">
        <h1>CheatSheet Maker</h1>
      </div>
      <div className="layout">
        <div className="upload-column">
          <FileUpload />
        </div>
        <div className="info-column">
          <p>Upload lecture notes or slides, and the app extracts the key definitions, theorems, formulas and examples, shortens the wording while keeping the math intact, and compiles a print-ready PDF based on your format settings.</p>

          <h2>How to use it</h2>
          <ol>
            <li>Upload your files </li>
            <li>Set your format settings</li>
            <li>Click generate</li>
          </ol>
        </div>
      </div>
    </div>
  );
}


export default App;