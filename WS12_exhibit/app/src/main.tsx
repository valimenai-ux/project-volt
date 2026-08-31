import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { C, F } from './theme'

const style = document.createElement('style')
style.textContent = `
  *{box-sizing:border-box}
  html,body{margin:0;padding:0}
  body{background:${C.page};color:${C.text};font-family:${F.sans};
       -webkit-font-smoothing:antialiased}
  a{color:${C.electrical};text-decoration:none}
  a:hover{color:${C.electricalLo}}
  button{font-family:inherit}
  ::-webkit-scrollbar{width:10px;height:10px}
  ::-webkit-scrollbar-track{background:${C.page}}
  ::-webkit-scrollbar-thumb{background:${C.lineHard}}
  input[type=range]{-webkit-appearance:none;appearance:none;height:2px;
    background:${C.lineHard};outline:none}
  input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;
    width:12px;height:12px;background:${C.electrical};cursor:pointer}
  input[type=range]::-moz-range-thumb{width:12px;height:12px;border:0;
    background:${C.electrical};cursor:pointer}
`
document.head.appendChild(style)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
