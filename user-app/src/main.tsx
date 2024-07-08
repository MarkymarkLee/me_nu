import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { createTheme, ThemeProvider } from "@material-ui/core/styles";
import { orange, red } from "@material-ui/core/colors";
import { firebaseConfig } from "./secret";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
if (app == null) {
  throw new Error("Firebase app initialization failed.");
}
export const db = getFirestore(app);
if (db == null) {
  throw new Error("Firestore initialization failed.");
}

// const analytics = getAnalytics(app);
const theme = createTheme({
  palette: {
    primary: orange,
    secondary: {
      main: '#ff9800',
    },
  },
});

ReactDOM.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}><App /></ThemeProvider>;
  </React.StrictMode>,
  document.getElementById("root")
);

