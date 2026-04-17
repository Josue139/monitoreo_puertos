import React,{useEffect,useState} from 'react';
import axios from 'axios';

export default function PortTable({selectedPort}){
  const [ips,setIps]=useState([]);
  const [loading,setLoading]=useState(null);
  const [scanResult,setScanResult]=useState(null);

  useEffect(()=>{
    // CORREGIDO: Ruta relativa
    const url=selectedPort
      ? `/api/top-ips?port=${selectedPort}`
      : `/api/top-ips`;
    axios.get(url).then(res=>setIps(res.data));
  },[selectedPort]);

  const runNmap=async(ip)=>{
    setLoading(ip);
    try{
      // CORREGIDO: Ruta relativa
      const res=await axios.get(`/api/scan-target?ip=${ip}`);
      setScanResult({ip,data:res.data});
    }catch(e){alert("Error en escaneo");}
    setLoading(null);
  };

  return(
    <div style={{background:'#111113',padding:'24px',borderRadius:'12px',border:'1px solid #1c1c1f'}}>
      <h3 style={{color:'#fff',fontSize:'13px',marginBottom:'20px',fontWeight:600}}>
        {selectedPort?`TOP IPS BY PORT ACCESS: ${selectedPort}`:"TOP IPS BY PORT ACCESS: GLOBAL"}
      </h3>

      <table style={{width:'100%',color:'#a1a1aa',fontSize:'12px',borderCollapse:'collapse'}}>
        <thead>
          <tr style={{borderBottom:'1px solid #1c1c1f',textAlign:'left',color:'#52525b'}}>
            <th style={{padding:'12px'}}>ORIGIN IP</th>
            <th style={{padding:'12px'}}>HOSTNAME (DNS)</th>
            <th style={{padding:'12px'}}>PORT</th>
            <th style={{padding:'12px'}}>TOTAL REQUESTS</th>
            <th style={{padding:'12px'}}>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          {ips.map((item,i)=>(
            <tr key={i} style={{borderBottom:'1px solid #111113'}}>
              <td style={{padding:'12px',color:'#fff'}}>{item.ip}</td>
              <td style={{padding:'12px',color:'#00d2ff'}}>{item.hostname}</td>
              <td style={{padding:'12px',color:'#00d2ff',fontWeight:'bold'}}>{item.port}</td>
              <td style={{padding:'12px',color:'#fff',fontWeight:'bold'}}>{item.count}</td>
              <td style={{padding:'12px'}}>
                <button
                  onClick={()=>runNmap(item.ip)}
                  disabled={loading===item.ip}
                  style={{background:'#3b82f6',color:'#fff',border:'none',padding:'5px 12px',borderRadius:'6px',cursor:'pointer',fontSize:'11px',fontWeight:600}}
                >
                  {loading===item.ip?'Escaneando...':'NMAP SCAN'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {scanResult&&(
        <div style={{position:'fixed',top:'50px',left:'50px',width:'400px',background:'#000',padding:'20px',border:'1px solid #333',borderRadius:'8px',zIndex:100}}>
          <h4 style={{color:'#fff',margin:'0 0 10px 0'}}>Banner Grabbing: {scanResult.ip}</h4>
          <pre style={{color:'#00d2ff',fontSize:'11px',whiteSpace:'pre-wrap',maxHeight:'200px',overflowY:'auto'}}>
            {JSON.stringify(scanResult.data,null,2)}
          </pre>
          <button onClick={()=>setScanResult(null)} style={{background:'#27272a',color:'#fff',border:'none',padding:'4px 8px',borderRadius:'4px',cursor:'pointer',marginTop:'10px'}}>Cerrar</button>
        </div>
      )}
    </div>
  );
}
