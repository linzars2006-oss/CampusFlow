import './App.css';
import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

const api = 'http://localhost:8080';

function App() {
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loggedInUser, setLoggedInUser] = useState(null);

  const handleLogin = async () => {
    if (!email || !password) return alert("Please fill in all fields.");
    try {
      const res = await fetch(`${api}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok) {
        setLoggedInUser(data.user);
        setShowLogin(false);
        setEmail('');
        setPassword('');
        alert("Login successful!");
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert("Error logging in. Please try again.");
    }
  };

  const handleSignup = async () => {
    if (!email || !password || !name) return alert("Please fill in all fields.");
    try {
      const res = await fetch(`${api}/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name })
      });
      const data = await res.json();
      if (res.ok) {
        alert("Signup successful! Please login.");
        setShowSignup(false);
        setShowLogin(true);
        setEmail('');
        setPassword('');
        setName('');
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert("Error signing up. Please try again.");
    }
  };

  const handleLogout = () => {
    setLoggedInUser(null);
  };

  return (
    <Router>
      <header className="header">
        <h2><b>KONGU ENGINEERING COLLEGE</b></h2>
        <p>(Autonomous)</p>
        <p>PERUNDURAI, ERODE-638060 TAMILNADU INDIA</p>

        <div className="auth-buttons">
          {!loggedInUser ? (
            <>
              <button className="btn btn-secondary" onClick={() => setShowLogin(true)}>Login</button>
              <button className="btn btn-secondary" onClick={() => setShowSignup(true)}>Sign Up</button>
            </>
          ) : (
            <>
              <span className="welcome-text">Welcome, {loggedInUser.name}!</span>
              <button className="btn btn-secondary" onClick={handleLogout}>Logout</button>
            </>
          )}
        </div>

        <a href="https://www.kongu.edu" target="_blank" rel="noopener noreferrer">www.kongu.edu</a>
      </header>

      {showLogin && !loggedInUser && (
        <div className="login-modal">
          <div className="login-box">
            <h3>Login</h3>
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <button className="btn btn-primary" onClick={handleLogin}>Login</button>
            <button className="btn btn-link" onClick={() => { setShowLogin(false); setShowSignup(true); }}>Need an account? Sign up</button>
          </div>
        </div>
      )}

      {showSignup && !loggedInUser && (
        <div className="login-modal">
          <div className="login-box">
            <h3>Sign Up</h3>
            <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <button className="btn btn-primary" onClick={handleSignup}>Register</button>
            <button className="btn btn-link" onClick={() => { setShowSignup(false); setShowLogin(true); }}>Already have an account? Login</button>
          </div>
        </div>
      )}

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/student-details" element={<StudentDetails />} />
        <Route path="/exam-details" element={<ExamDetails />} />
        <Route path="/fees-payments" element={<FeesPayments />} />
      </Routes>
    </Router>
  );
}

function Home() {
  return (
    <div className="nav-container">
      <Link to="/student-details" className="nav-box" style={{ backgroundColor: '#c9a8dd' }}>
        <div>Student<br />Details</div>
        <button className="btn btn-light">View</button>
      </Link>

      <Link to="/fees-payments" className="nav-box" style={{ backgroundColor: '#d2942d' }}>
        <div>Fees<br />Payments</div>
        <button className="btn btn-light">View</button>
      </Link>

      <Link to="/exam-details" className="nav-box" style={{ backgroundColor: '#2d9cd2' }}>
        <div>Exam<br />Details</div>
        <button className="btn btn-light">View</button>
      </Link>
    </div>
  );
}

function StudentDetails() {
  const [createRno, setCreateRno] = useState('');
  const [createName, setCreateName] = useState('');
  const [createStay, setCreateStay] = useState('dayscholars');

  const [readRno, setReadRno] = useState('');
  const [readResult, setReadResult] = useState('');

  const [updateRno, setUpdateRno] = useState('');
  const [updateName, setUpdateName] = useState('');
  const [updateStay, setUpdateStay] = useState('dayscholars');

  const [deleteRno, setDeleteRno] = useState('');

  const createStudent = async () => {
    const rno = parseInt(createRno);
    const res = await fetch(`${api}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rno, name: createName, stay: createStay })
    });

    const data = await res.json();
    alert(data.message);
  };

  const readStudent = async () => {
    const rno = parseInt(readRno);
    const res = await fetch(`${api}/fetch?rno=${rno}`);
    const data = await res.json();
    setReadResult(res.ok ? `Name: ${data.student.name}, Stay: ${data.student.stay}` : data.message);
  };

  const updateStudent = async () => {
    const rno = parseInt(updateRno);
    const res = await fetch(`${api}/update`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rno, name: updateName, stay: updateStay })
    });

    const data = await res.json();
    alert(data.message);
  };

  const deleteStudent = async () => {
    const rno = parseInt(deleteRno);
    const res = await fetch(`${api}/delete?rno=${rno}`, { method: 'DELETE' });
    const data = await res.json();
    alert(data.message);
  };

  return (
    <div className="main-content">
      <h2>Student Details Management</h2>

      <section>
        <h3>Enter Student Details</h3>
        <div className="form-row">
          <input value={createRno} onChange={e => setCreateRno(e.target.value)} placeholder="Rno" />
          <input value={createName} onChange={e => setCreateName(e.target.value)} placeholder="Name" />
          <select value={createStay} onChange={e => setCreateStay(e.target.value)}>
            <option value="dayscholars">Day Scholar</option>
            <option value="hostel">Hostel</option>
          </select>
          <button onClick={createStudent}>Submit</button>
        </div>
      </section>

      <section>
        <h3>View Student Details</h3>
        <div className="form-row">
          <input value={readRno} onChange={e => setReadRno(e.target.value)} placeholder="Rno" />
          <button onClick={readStudent}>Show</button>
        </div>
        <p>{readResult}</p>
      </section>

      <section>
        <h3>Update Student Details</h3>
        <div className="form-row">
          <input value={updateRno} onChange={e => setUpdateRno(e.target.value)} placeholder="Rno" />
          <input value={updateName} onChange={e => setUpdateName(e.target.value)} placeholder="New Name" />
          <select value={updateStay} onChange={e => setUpdateStay(e.target.value)}>
            <option value="dayscholars">Day Scholar</option>
            <option value="hostel">Hostel</option>
          </select>
          <button onClick={updateStudent}>Update</button>
        </div>
      </section>

      <section>
        <h3>Delete Student Details</h3>
        <div className="form-row">
          <input value={deleteRno} onChange={e => setDeleteRno(e.target.value)} placeholder="Rno" />
          <button onClick={deleteStudent}>Delete</button>
        </div>
      </section>
    </div>
  );
}

function ExamDetails() {
  return (
    <div className="main-content" style={{ padding: '20px' }}>
      <h2>Machine Learning Course Details</h2>

      <h3>1st Year</h3>
      <table>
        <thead><tr><th>Semester</th><th>Subject</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td>Sem 1</td><td>Programming in C</td><td>Basics of C programming</td></tr>
          <tr><td>Sem 1</td><td>Mathematics and Linear Algebra</td><td>Statistics and probability fundamentals</td></tr>
          <tr><td>Sem 2</td><td>Data Structures</td><td>Arrays, Trees, Graphs</td></tr>
          <tr><td>Sem 2</td><td>Python Programming</td><td>Basic Python</td></tr>
        </tbody>
      </table>

      <h3>2nd Year</h3>
      <table>
        <thead><tr><th>Semester</th><th>Subject</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td>Sem 3</td><td>Probability & Statistics</td><td>Hypothesis testing, distributions</td></tr>
          <tr><td>Sem 3</td><td>Data Processing</td><td>Numpy, Pandas, Matplotlib</td></tr>
          <tr><td>Sem 4</td><td>Machine Learning</td><td>Supervised/unsupervised models</td></tr>
          <tr><td>Sem 4</td><td>Java Programming</td><td>Advanced Java</td></tr>
        </tbody>
      </table>

      <h3>3rd Year</h3>
      <table>
        <thead><tr><th>Semester</th><th>Subject</th><th>Description</th></tr></thead>
        <tbody>
          <tr><td>Sem 5</td><td>Advanced Machine Learning</td><td>Model tuning, ensembles</td></tr>
          <tr><td>Sem 5</td><td>Natural Language Processing</td><td>Text classification, transformers</td></tr>
          <tr><td>Sem 6</td><td>Deep Learning</td><td>Neural nets using TensorFlow</td></tr>
          <tr><td>Sem 6</td><td>Project Work</td><td>ML Capstone Project</td></tr>
        </tbody>
      </table>
    </div>
  );
}

function FeesPayments() {
  const [rno, setRno] = useState('');
  const [feeDetails, setFeeDetails] = useState(null);

  const fetchFeeDetails = async () => {
    if (!rno) return alert("Please enter Roll Number");
    try {
      const res = await fetch(`${api}/fetch?rno=${rno}`);
      const data = await res.json();
      if (res.ok) {
        setFeeDetails(data.student);
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert("Error fetching fee details");
    }
  };

  return (
    <div className="main-content">
      <h2>Fee Payment Details</h2>
      
      <section>
        <h3>View Fee Details</h3>
        <div className="form-row">
          <input 
            value={rno} 
            onChange={e => setRno(e.target.value)} 
            placeholder="Enter Roll Number" 
          />
          <button onClick={fetchFeeDetails}>Show Details</button>
        </div>
        
        {feeDetails && (
          <div className="fee-details">
            <h4>Student Information</h4>
            <p>Roll Number: {feeDetails.rno}</p>
            <p>Name: {feeDetails.name}</p>
            <p>Stay Type: {feeDetails.stay}</p>
            
            <h4>Fee Structure</h4>
            {feeDetails.stay === 'hostel' ? (
              <>
                <p>Tuition Fee: 50,000</p>
                <p>Hostel Fee: 30,000</p>
                <p>Total Fee: 80,000</p>
              </>
            ) : (
              <>
                <p>Tuition Fee: 50,000</p>
                <p>Bus fees: 27,000</p>
                <p>Total Fee: 77,000</p>
              </>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

export default App;
