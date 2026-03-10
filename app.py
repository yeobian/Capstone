import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Upload, 
  Zap, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Info,
  Maximize2,
  Cpu
} from 'lucide-react';

const CLASS_NAMES = {
  0: "T-shirt/top",
  1: "Trouser",
  2: "Pullover",
  3: "Dress",
  4: "Coat",
  5: "Sandal",
  6: "Shirt",
  7: "Sneaker",
  8: "Bag",
  9: "Ankle boot"
};

const App = () => {
  // State management
  const [modelWeights, setModelWeights] = useState("models/baseline_v2.pth");
  const [numClasses, setNumClasses] = useState(10);
  const [isModelLoaded, setIsModelLoaded] = useState(true);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [results, setResults] = useState(null);

  // Mock scan function
  const handleScan = () => {
    setIsScanning(true);
    setResults(null);
    
    // Simulate neural network processing time
    setTimeout(() => {
      const mockProbs = Array.from({ length: 10 }, () => Math.random());
      const sum = mockProbs.reduce((a, b) => a + b, 0);
      const normalizedProbs = mockProbs.map(p => p / sum);
      
      // Ensure one is clearly the winner for the demo
      const winnerIdx = Math.floor(Math.random() * 10);
      normalizedProbs[winnerIdx] = 0.7 + (Math.random() * 0.2);
      
      const finalSum = normalizedProbs.reduce((a, b) => a + b, 0);
      const finalProbs = normalizedProbs.map(p => p / finalSum);

      const sortedIndices = [...Array(10).keys()].sort((a, b) => finalProbs[b] - finalProbs[a]);
      
      setResults({
        probabilities: finalProbs,
        topIdx: sortedIndices[0],
        sortedIndices
      });
      setIsScanning(false);
    }, 1500);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (f) => {
        setUploadedImage(f.target.result);
        setResults(null);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 font-sans overflow-hidden selection:bg-cyan-500/30">
      {/* Ambient Background Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Sidebar */}
      <aside className="relative w-80 bg-slate-900/40 backdrop-blur-xl border-r border-slate-800/50 p-6 flex flex-col shrink-0 z-10">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <Settings className="w-5 h-5 text-cyan-400" />
          </div>
          <h3 className="text-lg font-semibold tracking-tight text-slate-100">Engine Settings</h3>
        </div>

        <div className="space-y-6 flex-grow">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Model Weights</label>
            <input 
              type="text" 
              value={modelWeights}
              onChange={(e) => setModelWeights(e.target.value)}
              className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all text-slate-300 shadow-inner"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Output Classes</label>
            <input 
              type="number" 
              value={numClasses}
              onChange={(e) => setNumClasses(parseInt(e.target.value))}
              className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all text-slate-300 shadow-inner"
            />
          </div>

          <div className="h-px w-full bg-gradient-to-r from-transparent via-slate-700/50 to-transparent my-6" />

          {isModelLoaded ? (
            <div className="flex items-center gap-3 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              Neural Engine Online
            </div>
          ) : (
            <div className="flex items-center gap-3 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-medium">
              <AlertCircle className="w-4 h-4" />
              Weights fail to load
            </div>
          )}
        </div>

        <div className="pt-4 mt-6">
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold flex items-center gap-2">
            <Cpu className="w-3 h-3" /> v2.0.0 Active
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="relative flex-grow overflow-y-auto p-8 lg:p-12 max-w-7xl mx-auto w-full z-10">
        <header className="mb-10">
          <h1 className="text-4xl lg:text-5xl font-extrabold mb-3 tracking-tight">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500">
              Wardrobe AI Vision
            </span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl font-light">
            Next-generation clothing classification powered by deep learning. Drop an item below to begin analysis.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 xl:gap-12">
          {/* Column 1: Input Stream */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 mb-4 px-1">
              <Upload className="w-5 h-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-slate-200">Input Stream</h3>
            </div>

            <div 
              className={`relative group rounded-3xl transition-all duration-300 flex flex-col items-center justify-center min-h-[450px] overflow-hidden
                ${uploadedImage 
                  ? 'bg-slate-900/40 border border-slate-700/50 shadow-2xl backdrop-blur-sm' 
                  : 'border-2 border-dashed border-slate-700 hover:border-cyan-500/50 bg-slate-900/20 hover:bg-slate-900/40 backdrop-blur-sm'
              }`}
            >
              {!uploadedImage ? (
                <>
                  <div className="p-4 bg-slate-800/50 rounded-full mb-4 group-hover:scale-110 group-hover:bg-cyan-500/10 transition-all duration-300">
                    <Upload className="w-8 h-8 text-cyan-400" />
                  </div>
                  <p className="text-slate-300 font-medium mb-1">Drag and drop your image</p>
                  <p className="text-slate-500 text-sm mb-6">Supports JPG, PNG, WEBP</p>
                  
                  <input 
                    type="file" 
                    onChange={handleFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    accept="image/*"
                  />
                  <button className="relative z-0 bg-slate-800 text-slate-200 px-6 py-2.5 rounded-full text-sm font-medium hover:bg-slate-700 hover:text-white transition-colors border border-slate-700 hover:border-slate-600 shadow-sm">
                    Browse Files
                  </button>
                </>
              ) : (
                <div className="relative w-full h-full flex items-center justify-center p-6">
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent to-slate-950/50 pointer-events-none" />
                  <img 
                    src={uploadedImage} 
                    alt="Uploaded" 
                    className="max-w-full max-h-[400px] w-auto h-auto rounded-xl shadow-2xl object-contain relative z-0"
                  />
                  <button 
                    onClick={() => {setUploadedImage(null); setResults(null);}}
                    className="absolute top-4 right-4 bg-slate-900/80 backdrop-blur-md p-2.5 rounded-full hover:bg-red-500/20 hover:text-red-400 text-slate-300 transition-all border border-slate-700/50 hover:border-red-500/30 z-20 group/btn"
                    title="Remove Image"
                  >
                    <Settings className="w-4 h-4 rotate-45 group-hover/btn:rotate-90 transition-transform duration-300" />
                  </button>
                </div>
              )}
            </div>
          </section>

          {/* Column 2: Analysis */}
          <section className="space-y-4">
            <div className="flex items-center gap-2 mb-4 px-1">
              <Zap className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-slate-200">Neural Analysis</h3>
            </div>

            {!uploadedImage ? (
              <div className="bg-slate-900/40 backdrop-blur-sm border border-slate-800 rounded-3xl p-8 flex flex-col items-center justify-center min-h-[450px] text-center">
                <div className="p-4 bg-blue-500/10 rounded-full mb-4">
                  <Info className="w-8 h-8 text-blue-400" />
                </div>
                <h4 className="text-slate-300 font-medium text-lg mb-2">Awaiting Visual Input</h4>
                <p className="text-slate-500 text-sm max-w-xs">
                  Upload a clothing item to the input stream to begin the neural classification process.
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <button 
                  onClick={handleScan}
                  disabled={isScanning}
                  className={`relative w-full py-4 rounded-2xl font-bold flex items-center justify-center gap-3 transition-all duration-300 overflow-hidden group ${
                    isScanning 
                      ? 'bg-slate-800 text-slate-400 cursor-not-allowed border border-slate-700 shadow-inner' 
                      : 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:shadow-lg hover:shadow-cyan-500/25 hover:-translate-y-0.5 border border-cyan-400/50'
                  }`}
                >
                  {isScanning ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      PROCESSING TENSORS...
                    </>
                  ) : (
                    <>
                      <Maximize2 className="w-5 h-5" />
                      INITIALIZE SCAN
                    </>
                  )}
                </button>

                {results && (
                  <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                    {/* Primary Match */}
                    <div className="relative overflow-hidden bg-slate-900/60 backdrop-blur-md border border-slate-700/50 rounded-3xl p-6 shadow-xl">
                      <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500" />
                      <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-4 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        Primary Match
                      </h4>
                      <div className="flex items-end justify-between">
                        <div>
                          <span className="text-3xl font-extrabold text-slate-100 tracking-tight">
                            {CLASS_NAMES[results.topIdx]}
                          </span>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-emerald-400 font-mono text-2xl font-bold">
                            {(results.probabilities[results.topIdx] * 100).toFixed(1)}%
                          </span>
                          <span className="text-slate-500 text-xs uppercase tracking-wider font-semibold">Confidence</span>
                        </div>
                      </div>
                    </div>

                    {/* Confidence Matrix */}
                    <div className="bg-slate-900/60 backdrop-blur-md border border-slate-700/50 rounded-3xl p-6 shadow-xl">
                      <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-6 flex items-center gap-2">
                        <Cpu className="w-4 h-4 text-cyan-500" />
                        Confidence Matrix
                      </h4>
                      <div className="space-y-4">
                        {Object.entries(CLASS_NAMES).map(([idx, name]) => {
                          const prob = results.probabilities[idx];
                          const isWinner = parseInt(idx) === results.topIdx;
                          return (
                            <div key={idx} className="space-y-1.5 group/row">
                              <div className="flex justify-between text-sm font-medium">
                                <span className={`${isWinner ? "text-cyan-400" : "text-slate-400 group-hover/row:text-slate-300"} transition-colors`}>
                                  {name}
                                </span>
                                <span className={`${isWinner ? "text-cyan-400" : "text-slate-500"} font-mono`}>
                                  {(prob * 100).toFixed(1)}%
                                </span>
                              </div>
                              <div className="h-2 bg-slate-950/50 rounded-full overflow-hidden border border-slate-800/50">
                                <div 
                                  className={`h-full transition-all duration-1000 ease-out relative ${
                                    isWinner 
                                      ? 'bg-gradient-to-r from-cyan-400 to-blue-500' 
                                      : 'bg-slate-700 group-hover/row:bg-slate-600'
                                  }`}
                                  style={{ width: `${Math.max(prob * 100, 1)}%` }}
                                >
                                  {isWinner && (
                                    <div className="absolute inset-0 bg-white/20 w-full" />
                                  )}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
};

export default App;
