import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Upload, 
  Search, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Info,
  Database,
  ThumbsUp,
  ThumbsDown,
  Layers
} from 'lucide-react';

const App = () => {
  // State management - adapted for Retrieval System
  const [embeddingModel, setEmbeddingModel] = useState("openai/clip-vit-base-patch32");
  const [vectorIndex, setVectorIndex] = useState("faiss_deepfashion_v1.index");
  const [topK, setTopK] = useState(4);
  const [isEngineOnline, setIsEngineOnline] = useState(true);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState(null);
  const [feedback, setFeedback] = useState({}); // Track user likes/dislikes

  // Mock catalog of images for retrieval simulation
  const MOCK_CATALOG = [
    { id: 'item_1042', img: 'https://images.unsplash.com/photo-1434389678232-04ce6cba3338?auto=format&fit=crop&w=400&q=80', score: 0.942 },
    { id: 'item_8912', img: 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=400&q=80', score: 0.891 },
    { id: 'item_3321', img: 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=400&q=80', score: 0.855 },
    { id: 'item_5541', img: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=400&q=80', score: 0.820 },
    { id: 'item_9921', img: 'https://images.unsplash.com/photo-1550639525-c97d455acf70?auto=format&fit=crop&w=400&q=80', score: 0.781 },
    { id: 'item_1102', img: 'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?auto=format&fit=crop&w=400&q=80', score: 0.745 },
  ];

  // Mock retrieval scan function
  const handleSearch = () => {
    setIsSearching(true);
    setResults(null);
    setFeedback({});
    
    // Simulate CLIP embedding generation and Faiss cosine similarity search
    setTimeout(() => {
      // Return top K items from the mock catalog
      setResults(MOCK_CATALOG.slice(0, topK));
      setIsSearching(false);
    }, 1800);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (f) => {
        setUploadedImage(f.target.result);
        setResults(null);
        setFeedback({});
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFeedback = (id, type) => {
    setFeedback(prev => ({
      ...prev,
      [id]: prev[id] === type ? null : type // toggle off if already selected
    }));
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 font-sans overflow-hidden selection:bg-cyan-500/30">
      {/* Ambient Background Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Sidebar - Configured for Retrieval */}
      <aside className="relative w-80 bg-slate-900/40 backdrop-blur-xl border-r border-slate-800/50 p-6 flex flex-col shrink-0 z-10">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <Settings className="w-5 h-5 text-cyan-400" />
          </div>
          <h3 className="text-lg font-semibold tracking-tight text-slate-100">Search Engine Config</h3>
        </div>

        <div className="space-y-6 flex-grow">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Embedding Model</label>
            <input 
              type="text" 
              value={embeddingModel}
              onChange={(e) => setEmbeddingModel(e.target.value)}
              className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all text-slate-300 shadow-inner"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Vector Index (Faiss)</label>
            <input 
              type="text" 
              value={vectorIndex}
              onChange={(e) => setVectorIndex(e.target.value)}
              className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all text-slate-300 shadow-inner"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Top-K Results</label>
            <input 
              type="number" 
              value={topK}
              min={1}
              max={6}
              onChange={(e) => setTopK(parseInt(e.target.value) || 4)}
              className="w-full bg-slate-950/50 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 transition-all text-slate-300 shadow-inner"
            />
          </div>

          <div className="h-px w-full bg-gradient-to-r from-transparent via-slate-700/50 to-transparent my-6" />

          {isEngineOnline ? (
            <div className="flex items-center gap-3 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              Vector Retrieval Ready
            </div>
          ) : (
            <div className="flex items-center gap-3 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-medium">
              <AlertCircle className="w-4 h-4" />
              Backend Offline
            </div>
          )}
        </div>

        <div className="pt-4 mt-6">
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold flex items-center gap-2">
            <Database className="w-3 h-3" /> DeepFashion Catalog V1
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="relative flex-grow overflow-y-auto p-8 lg:p-12 mx-auto w-full z-10">
        <header className="mb-10 max-w-6xl mx-auto">
          <h1 className="text-4xl lg:text-5xl font-extrabold mb-3 tracking-tight">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500">
              Wardrobe Intelligence
            </span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl font-light">
            Visual similarity retrieval. Upload a clothing item to embed and search the catalog using cosine similarity.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 xl:gap-12 max-w-6xl mx-auto">
          {/* Column 1: Input Stream */}
          <section className="space-y-4 lg:col-span-5">
            <div className="flex items-center gap-2 mb-4 px-1">
              <Upload className="w-5 h-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-slate-200">Query Image</h3>
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
                  <p className="text-slate-300 font-medium mb-1">Drag and drop your query</p>
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
                    alt="Uploaded query" 
                    className="max-w-full max-h-[400px] w-auto h-auto rounded-xl shadow-2xl object-contain relative z-0"
                  />
                  <button 
                    onClick={() => {setUploadedImage(null); setResults(null); setFeedback({});}}
                    className="absolute top-4 right-4 bg-slate-900/80 backdrop-blur-md p-2.5 rounded-full hover:bg-red-500/20 hover:text-red-400 text-slate-300 transition-all border border-slate-700/50 hover:border-red-500/30 z-20 group/btn"
                    title="Remove Image"
                  >
                    <Settings className="w-4 h-4 rotate-45 group-hover/btn:rotate-90 transition-transform duration-300" />
                  </button>
                </div>
              )}
            </div>
            
            {/* Search Trigger Button placed under the image for better flow */}
            {uploadedImage && (
               <button 
               onClick={handleSearch}
               disabled={isSearching}
               className={`relative w-full py-4 rounded-2xl font-bold flex items-center justify-center gap-3 transition-all duration-300 overflow-hidden group mt-4 ${
                 isSearching 
                   ? 'bg-slate-800 text-slate-400 cursor-not-allowed border border-slate-700 shadow-inner' 
                   : 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:shadow-lg hover:shadow-cyan-500/25 hover:-translate-y-0.5 border border-cyan-400/50'
               }`}
             >
               {isSearching ? (
                 <>
                   <Loader2 className="w-5 h-5 animate-spin" />
                   COMPUTING EMBEDDING...
                 </>
               ) : (
                 <>
                   <Search className="w-5 h-5" />
                   FIND SIMILAR ITEMS
                 </>
               )}
             </button>
            )}
          </section>

          {/* Column 2: Retrieval Results */}
          <section className="space-y-4 lg:col-span-7">
            <div className="flex items-center gap-2 mb-4 px-1">
              <Layers className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-semibold text-slate-200">Catalog Retrieval Matches</h3>
            </div>

            {!uploadedImage ? (
              <div className="bg-slate-900/40 backdrop-blur-sm border border-slate-800 rounded-3xl p-8 flex flex-col items-center justify-center min-h-[450px] text-center">
                <div className="p-4 bg-blue-500/10 rounded-full mb-4">
                  <Info className="w-8 h-8 text-blue-400" />
                </div>
                <h4 className="text-slate-300 font-medium text-lg mb-2">Awaiting Query Vector</h4>
                <p className="text-slate-500 text-sm max-w-sm">
                  Upload a clothing item to generate its CLIP embedding and retrieve visually similar garments from the catalog database.
                </p>
              </div>
            ) : !results && !isSearching ? (
               <div className="bg-slate-900/20 border border-slate-800/50 border-dashed rounded-3xl p-8 flex flex-col items-center justify-center min-h-[450px] text-center">
                 <Search className="w-12 h-12 text-slate-600 mb-4 opacity-50" />
                 <p className="text-slate-500 font-medium">Ready to search vector space.</p>
               </div>
            ) : isSearching ? (
              <div className="bg-slate-900/20 border border-slate-800/50 rounded-3xl p-8 flex flex-col items-center justify-center min-h-[450px] text-center">
                 <div className="flex items-center gap-4 text-cyan-400 font-mono">
                   <Loader2 className="w-8 h-8 animate-spin" />
                   <span>Calculating cosine similarities...</span>
                 </div>
               </div>
            ) : (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {results.map((item, index) => (
                    <div key={item.id} className="group relative bg-slate-900/60 backdrop-blur-md border border-slate-700/50 rounded-2xl overflow-hidden shadow-xl hover:border-cyan-500/50 transition-colors">
                      
                      {/* Badge for Score */}
                      <div className="absolute top-3 left-3 z-10 bg-slate-950/80 backdrop-blur-sm border border-slate-700 px-3 py-1 rounded-full flex items-center gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                        <span className="text-xs font-mono font-bold text-slate-200">
                          {(item.score * 100).toFixed(1)}% match
                        </span>
                      </div>

                      {/* Result Image (with fallback colored div) */}
                      <div className="aspect-[4/5] w-full bg-slate-800 relative overflow-hidden">
                        <img 
                          src={item.img} 
                          alt={`Similar item ${index + 1}`}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                        {/* Fallback if image fails to load */}
                        <div className="hidden absolute inset-0 bg-slate-800 items-center justify-center flex-col gap-2">
                          <Layers className="w-8 h-8 text-slate-600" />
                          <span className="text-xs text-slate-500">{item.id}</span>
                        </div>
                        
                        {/* Gradient overlay for bottom controls */}
                        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent opacity-80" />
                      </div>

                      {/* Feedback Controls */}
                      <div className="absolute bottom-0 left-0 right-0 p-4 flex items-center justify-between">
                        <span className="text-xs font-mono text-slate-400">{item.id}</span>
                        <div className="flex gap-2">
                          <button 
                            onClick={() => handleFeedback(item.id, 'like')}
                            className={`p-2 rounded-full backdrop-blur-md transition-all ${
                              feedback[item.id] === 'like' 
                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50' 
                                : 'bg-slate-800/80 text-slate-400 border border-slate-600 hover:bg-slate-700 hover:text-slate-200'
                            }`}
                          >
                            <ThumbsUp className="w-4 h-4" />
                          </button>
                          <button 
                            onClick={() => handleFeedback(item.id, 'dislike')}
                            className={`p-2 rounded-full backdrop-blur-md transition-all ${
                              feedback[item.id] === 'dislike' 
                                ? 'bg-red-500/20 text-red-400 border border-red-500/50' 
                                : 'bg-slate-800/80 text-slate-400 border border-slate-600 hover:bg-slate-700 hover:text-slate-200'
                            }`}
                          >
                            <ThumbsDown className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
};

export default App;
