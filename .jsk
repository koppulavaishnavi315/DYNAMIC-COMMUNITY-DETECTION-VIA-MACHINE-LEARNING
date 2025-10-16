import React, { useState } from "react";
import axios from "axios";
import * as d3 from "d3";

export default function App() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);

  const handleUpload = (e) => {
    setFiles([...e.target.files]);
  };

  const handleAnalyze = async () => {
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));
    const res = await axios.post("http://127.0.0.1:8000/analyze/", formData);
    setResults(res.data.results);
  };

  const drawGraph = (data, container) => {
    const width = 400, height = 300;
    const svg = d3.select(container).html("").append("svg")
      .attr("width", width)
      .attr("height", height);
    const nodes = Object.keys(data.communities).map(n => ({ id: +n, group: data.communities[n] }));
    const links = [];
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const simulation = d3.forceSimulation(nodes)
      .force("charge", d3.forceManyBody().strength(-30))
      .force("center", d3.forceCenter(width/2, height/2))
      .force("collision", d3.forceCollide(20))
      .on("tick", () => {
        svg.selectAll("circle").data(nodes).join("circle")
          .attr("r", 6)
          .attr("cx", d => d.x)
          .attr("cy", d => d.y)
          .attr("fill", d => color(d.group));
      });
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-center text-blue-700">Dynamic Community Detection</h1>
      <input type="file" multiple accept=".csv" onChange={handleUpload} />
      <button onClick={handleAnalyze} className="bg-blue-600 text-white px-4 py-2 rounded">Analyze</button>

      <div className="grid grid-cols-2 gap-4">
        {results.map((r, idx) => (
          <div key={idx} className="border p-4 rounded shadow">
            <h2 className="text-lg font-semibold">Snapshot {r.snapshot}</h2>
            <p>Modularity: {r.modularity}</p>
            <div id={`graph-${idx}`} ref={el => el && drawGraph(r, el)}></div>
          </div>
        ))}
      </div>
    </div>
  );
}
