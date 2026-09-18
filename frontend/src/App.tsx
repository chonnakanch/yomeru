import { SelectionCanvas } from './components/SelectionCanvas';

function App() {
  const handleCapture = (base64Image: string) => {
    console.log('Captured image:', base64Image.substring(0, 50) + '...');
  };

  return <SelectionCanvas onCapture={handleCapture} />;
}

export default App;
