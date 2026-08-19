import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: 'AIzaSyD0d1g1cu4w7PU3sEHbSyn0xnBptHh8ze0',
  authDomain: 'cutoff-guide-ai.firebaseapp.com',
  projectId: 'cutoff-guide-ai',
  storageBucket: 'cutoff-guide-ai.firebasestorage.app',
  messagingSenderId: '972640056313',
  appId: '1:972640056313:web:5a867d1b24652423a20328',
  measurementId: 'G-FYZTPWEL8C',
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account',
});

export default app;