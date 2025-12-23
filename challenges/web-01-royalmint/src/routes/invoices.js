const express = require("express");
const { pool } = require("../storage/db");

const router = express.Router();

// Vulnerable endpoint: fetches invoice by id but DOES NOT enforce ownership.
router.get("/:id", async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isFinite(id)) return res.status(400).send("bad id");

  const { rows } = await pool.query(
    "SELECT id, user_id, amount, note FROM invoices WHERE id = $1",
    [id]
  );
  const inv = rows[0];
  if (!inv) return res.status(404).send("not found");

  // Intended missing check (for a fixed version):
  // if (inv.user_id !== req.user.id && req.user.role !== 'admin') return res.status(403).send("forbidden");

  // Get username for the invoice owner
  const userRows = await pool.query("SELECT username FROM users WHERE id = $1", [inv.user_id]);
  const owner = userRows.rows[0];

  if (req.headers['accept']?.includes('application/json') || req.query.format === 'json') {
    return res.json({ 
      invoice: {
        id: inv.id,
        user_id: inv.user_id,
        owner: owner?.username || 'unknown',
        amount: inv.amount,
        note: inv.note
      }
    });
  }

  res.render("invoice", { user: req.user, inv });
});

module.exports = router;
