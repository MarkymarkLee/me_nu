import { useEffect, useState } from "react";
import liff from "@line/liff";
import "./App.css";
import { CircularProgress } from "@material-ui/core";
import UserPreference from "./components/UserPreference";

export interface UserPreferenceProps {
  likedFood: string[];
  dislikedFood: string[];
  cannotEatFood: string[];
}

export interface Profile {
  userId: string;
  displayName: string;
  pictureUrl?: string;
  statusMessage?: string;
  userCharacter?: string;
  userState?: number;
  user_init_qa_count?: number;
  images?: string[];
  rec_count?: number;
  chat?: string[];
  last_chat_time?: string;
  preferences: UserPreferenceProps;
}

const useLiff = (liffId: string) => {
  const [userProfile, setUserProfile] = useState<Profile | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    liff.init({ liffId: liffId })
      .then(() => {
        setLoading(false);
        if (!liff.isInClient()) {
          setUserProfile({
            userId: 'test_user',
            displayName: 'Demo User',
            preferences: {
              likedFood: [],
              dislikedFood: [],
              cannotEatFood: [],
            },
          });
          return;
        }
        if (!liff.isLoggedIn()) {
          liff.login();
        } else {
          liff.getProfile().then(profile => {
            setUserProfile({
              userId: profile.userId,
              displayName: profile.displayName,
              pictureUrl: profile.pictureUrl,
              preferences: {
                likedFood: [],
                dislikedFood: [],
                cannotEatFood: [],
              },
            });
          });
        }
      })
      .catch(e => {
        setError(`LIFF init failed: ${e.message}`);
        setLoading(false);
      });
  }, [liffId]);

  return { userProfile, error, loading };
};


function App() {
  const { userProfile, error, loading } = useLiff(import.meta.env.VITE_LIFF_ID);

  if (loading) {
    return <div className="App">
      <CircularProgress />
      <p>Loading Line SDK...</p>
    </div>;
  }

  return (
    <div className="App">
      {userProfile && <UserPreference {...userProfile} />}
    </div>
  );
}

export default App;
