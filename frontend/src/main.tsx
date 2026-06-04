import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import { TerminalDataProvider } from "./hooks/useTerminalData";
import "./styles/globals.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <TerminalDataProvider>
      <App />
    </TerminalDataProvider>
  </React.StrictMode>
);
