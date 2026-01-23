import { Routes, Route } from "react-router-dom";
import LandingPage from "./components/Landing";
import MatchTeamCreator from "./components/Matchteamcreator";
import MyTeams from "./components/Myteam";
import Navbar from "./components/Navbar";
import Login from "./components/Login";
import Register from "./components/Register";
import Players from "./components/Players";
import FantasyMatchList from "./components/FantasyMatchList";
import FantasySelectPlayers from "./components/FantasySelectplayers";
import FantasyViewTeam from "./components/Fantasyviewteam";
import FantasyResults from "./components/Fantasyresult";

function App() {
  return (
    <>
      <Navbar />
      <div className="pt-16">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/create/:matchId" element={<MatchTeamCreator />} />
          <Route path="/my-teams" element={<MyTeams />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/players" element={<Players />} />
          <Route path="/fantasy" element={<FantasyMatchList />} />

          <Route
            path="/fantasy/select/:matchId"
            element={<FantasySelectPlayers />}
          />
          <Route path="/fantasy/view/:matchId" element={<FantasyViewTeam />} />
          <Route
            path="/fantasy/results/:matchId"
            element={<FantasyResults />}
          />
        </Routes>
      </div>
    </>
  );
}

export default App;
