require("dotenv").config();
const express = require("express");
const session = require("express-session");
const path = require("path");

const authRoutes = require("./routes/auth");
const previewRoutes = require("./routes/preview");
const { requireLogin } = require("./routes/middleware");

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "..", "views"));

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, "..", "public")));

app.use(session({
  secret: process.env.SESSION_SECRET || "dev-secret",
  resave: false,
  saveUninitialized: false,
  cookie: { httpOnly: true }
}));

app.use((req, _res, next) => {
  req.user = req.session.user || null;
  next();
});

app.get("/", (req, res) => res.render("index", { user: req.user }));

app.use("/auth", authRoutes);

app.get("/settings", requireLogin, (req, res) => {
  // INTENTIONAL LEAK: internal token is visible to authenticated users.
  res.render("settings", {
    user: req.user,
    internalToken: process.env.INTERNAL_TOKEN || "INTERNAL-TOKEN-missing"
  });
});

app.use("/preview", requireLogin, previewRoutes);

const port = Number(process.env.PORT || 3000);
app.listen(port, () => console.log(`[🎭 La Casa de Papel - Safe House Network] listening on ${port}`));
