import { Routes, Route, useLocation } from "react-router-dom";
import LandingPage from "./components/Landing";
import MatchTeamCreator from "./components/Matchteamcreator";
import MyTeams from "./components/Myteam";
import Navbar from "./components/Navbar";
import Login from "./components/Login";
import Register from "./components/Register";
import Players from "./components/Players";
import FantasySelectPlayers from "./components/FantasySelectplayers";
import FantasyViewTeam from "./components/Fantasyviewteam";
import FantasyResults from "./components/Fantasyresult";
import { useNavigate } from "react-router-dom";

// Admin components
import AdminLogin from "./admin/Adminlogin";
import AdminProtectedRoute from "./admin/AdminProtectedRoute.tsx";
import AdminDashboard from "./admin/AdminPanel";
import AdminTeams from "./admin/Teams";
import AdminPlayers from "./admin/Players";
import AdminMatches from "./admin/Matches";
import AdminNavbar from "./admin/Navbar";
import AdminMatchPlayers from "./admin/MatchPlayer"; 
import AdminMatchStats from "./admin/MatchStats.tsx";



import Upcomingmatches from "./components/Upcomingmatches.tsx";
import MatchdayLeaderboard from "./components/Matchdayleaderboard.tsx";
import OverallLeaderboard from "./components/Leaderboard.tsx";

function App() {
  const location = useLocation();
  const isAdmin =
    location.pathname.startsWith("/admin") &&
    location.pathname !== "/admin/login";
  const navigate = useNavigate();
  return (
    <>
      {/* Show AdminNavbar only for admin routes */}
      {isAdmin ? <AdminNavbar /> : <Navbar />}
      <div className="pt-16">
        <Routes>
          {/* Public / User Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/create/:matchId" element={<MatchTeamCreator />} />
          <Route path="/my-teams" element={<MyTeams />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/players" element={<Players />} />
          <Route path="/upcoming-matches" element={<Upcomingmatches />} />
          <Route path="/leaderboard" element={<OverallLeaderboard />} />
          <Route
            path="/leaderboard/match/:matchId"
            element={<MatchdayLeaderboard />}
          />
          <Route
            path="/fantasy/select/:matchId"
            element={<FantasySelectPlayers />}
          />
          <Route path="/fantasy/view/:matchId" element={<FantasyViewTeam />} />
          <Route
            path="/fantasy/results/:matchId"
            element={<FantasyResults />}
          />

          {/* Admin Routes */}
          {/* Admin Routes */}
          <Route
            path="/admin/login"
            element={<AdminLogin onLogin={() => navigate("/admin")} />}
          />

          <Route
            path="/admin"
            element={
              <AdminProtectedRoute>
                <AdminDashboard />
              </AdminProtectedRoute>
            }
          />

          <Route
            path="/admin/teams"
            element={
              <AdminProtectedRoute>
                <AdminTeams />
              </AdminProtectedRoute>
            }
          />

          <Route
            path="/admin/players"
            element={
              <AdminProtectedRoute>
                <AdminPlayers />
              </AdminProtectedRoute>
            }
          />

          <Route
            path="/admin/matches"
            element={
              <AdminProtectedRoute>
                <AdminMatches />
              </AdminProtectedRoute>
            }
          />
          <Route
            path="/admin/matches/:matchId/players"
            element={
              <AdminProtectedRoute>
                <AdminMatchPlayers />
              </AdminProtectedRoute>
            }
          />
          <Route
            path="/admin/matches/:matchId/stats"
            element={
              <AdminProtectedRoute>
                <AdminMatchStats />
              </AdminProtectedRoute>
            }
          />


        </Routes>
        
      </div>
    </>
  );
}

export default App;
