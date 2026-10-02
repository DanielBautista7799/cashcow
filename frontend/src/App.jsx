import Login from "./components/auth/Login";
import Dashboard from "./components/layout/Dashboard";
import { useAuth } from "./context/AuthContext";


function App() {
  const { token } = useAuth();

  if (!token) {
    return <Login />;
  }

  return <Dashboard />;
}

export default App;