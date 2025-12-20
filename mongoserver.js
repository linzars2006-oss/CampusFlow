import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors';
import bcrypt from 'bcryptjs';

const app = express();
const PORT = 8080; // Match frontend

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

mongoose.connect("mongodb://127.0.0.1:27017/linza", {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
  .then(() => console.log("✅ Connected to MongoDB"))
  .catch(err => console.error("❌ MongoDB connection error:", err));

const userSchema = new mongoose.Schema({
  rno: { type: Number, required: true, unique: true },
  name: { type: String, required: true },
  stay: { type: String, required: true, enum: ["dayscholars", "hostel"] },
});

const User = mongoose.model("MyStudent", userSchema);

// User Authentication Schema
const authSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  name: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

const AuthUser = mongoose.model("AuthUser", authSchema);

app.post("/submit", async (req, res) => {
  try {
    const { rno, name, stay } = req.body;
    const newStudent = new User({ rno, name, stay });
    await newStudent.save();
    res.status(201).json({ message: "Student data saved successfully", newStudent });
  } catch (error) {
    res.status(500).json({ message: "Error saving student", error: error.message });
  }
});

app.get("/fetch", async (req, res) => {
  try {
    const rno = parseInt(req.query.rno);
    const student = await User.findOne({ rno });
    if (!student) {
      return res.status(404).json({ message: "Student not found" });
    }
    res.status(200).json({ message: "Student found", student });
  } catch (err) {
    res.status(500).json({ message: "Server Error", error: err.message });
  }
});

app.put("/update", async (req, res) => {
  try {
    const { rno, name, stay } = req.body;
    const updated = await User.findOneAndUpdate({ rno }, { name, stay }, { new: true });
    if (!updated) {
      return res.status(404).json({ message: "Student not found for update" });
    }
    res.status(200).json({ message: "Student updated successfully", updated });
  } catch (error) {
    res.status(500).json({ message: "Error updating student", error: error.message });
  }
});

app.delete("/delete", async (req, res) => {
  try {
    const rno = parseInt(req.query.rno);
    const deleted = await User.findOneAndDelete({ rno });
    if (!deleted) {
      return res.status(404).json({ message: "Student not found for deletion" });
    }
    res.status(200).json({ message: "Student deleted successfully", deleted });
  } catch (error) {
    res.status(500).json({ message: "Error deleting student", error: error.message });
  }
});

// Signup endpoint
app.post("/signup", async (req, res) => {
  try {
    const { email, password, name } = req.body;
    
    // Check if user already exists
    const existingUser = await AuthUser.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: "User already exists" });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // Create new user
    const newUser = new AuthUser({
      email,
      password: hashedPassword,
      name
    });
    
    await newUser.save();
    res.status(201).json({ message: "User created successfully" });
  } catch (error) {
    res.status(500).json({ message: "Error creating user", error: error.message });
  }
});

// Login endpoint
app.post("/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user
    const user = await AuthUser.findOne({ email });
    if (!user) {
      return res.status(404).json({ message: "User not found" });
    }
    
    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ message: "Invalid password" });
    }
    
    res.status(200).json({ 
      message: "Login successful",
      user: {
        email: user.email,
        name: user.name
      }
    });
  } catch (error) {
    res.status(500).json({ message: "Error logging in", error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Server is running on http://localhost:${PORT}`);
});