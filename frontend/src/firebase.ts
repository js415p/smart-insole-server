import { initializeApp } from "firebase/app";
import { getDatabase, ref, onValue } from "firebase/database";

// These should be in .env for production
const firebaseConfig = {
  apiKey: "YOUR_API_KEY", // Note: API Key is usually not in .env for Admin SDK setup, but needed for client SDK
  authDomain: "smartsoledb.firebaseapp.com",
  databaseURL: "https://smartsoledb-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "smartsoledb",
  storageBucket: "smartsoledb.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
export const db = getDatabase(app);

export const subscribeToLiveUpdates = (userName: string, callback: (data: any) => void) => {
  const liveRef = ref(db, `insole_live/${userName}`);
  return onValue(liveRef, (snapshot) => {
    if (snapshot.exists()) {
      callback(snapshot.val());
    }
  });
};

export const subscribeToHistory = (userName: string, callback: (data: any) => void) => {
  const historyRef = ref(db, `insole_history/${userName}`);
  return onValue(historyRef, (snapshot) => {
    if (snapshot.exists()) {
      callback(snapshot.val());
    }
  });
};
