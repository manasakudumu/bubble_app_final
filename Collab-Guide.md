## 📝 Collaborative GitHub Workflow Guide

### For Small Group Collaboration Using VS Code & GitHub Classroom

---

### 👩‍🏫 Instructor Setup

- You've been assigned to a **group project via GitHub Classroom**.
- The repository already contains a working app written by your instructor.
- Your task:
  👉 *Each student makes two small improvements to the app (e.g., new feature, bug fix, or design tweak).* 

---

## 💻 Step-by-Step Instructions

> You can choose to use the **GUI (GitHub integration in VS Code)** or the **Terminal inside VS Code**. Both methods are shown.

---

### 🎠 Part 1: Setup – Clone the Repository

#### Using the VS Code GUI

1. Open **VS Code**.
2. Go to **View → Command Palette → Git: Clone**.
3. Paste the repository URL (from GitHub Classroom).
4. Choose a folder to save it locally.
5. Click “Open” when prompted.

#### Using the VS Code Terminal

```bash
git clone https://github.com/org-name/group-repo.git
cd group-repo
code .
```
**Note:** You will have to use the URL of the repo you get from Github classroom.
---

### 🌿 Part 2: Create a Branch for Your Work

> This prevents overwriting others’ work and lets you propose changes safely.

#### GUI Method

1. Click the **branch icon** in the bottom-left of VS Code.
2. Click **"Create new branch"**.
3. Name it something like `alex-fix-button` or `jamal-add-footer`.

#### Terminal Method

```bash
git checkout -b your-branch-name
```

---

### 🛠️ Part 3: Make Your Changes (Two Small Improvements)

- Edit code, text, or design elements in the app.
- Test your changes locally.
- Save your work often.

Examples:
- Change button text
- Add a new paragraph
- Adjust layout or fix a bug

---

### 📂 Part 4: Stage and Commit Your Changes

#### GUI Method

1. Go to the **Source Control** panel in the sidebar.
2. You’ll see a list of files you changed.
3. Add a message like `Add About section` or `Fix image layout`.
4. Click **✓ Commit**.

#### Terminal Method

```bash
git add .
git commit -m "Describe your changes here"
```

---

### 🚀 Part 5: Push Your Branch to GitHub

#### GUI Method

1. Click the **three dots** in the Source Control panel.
2. Choose **Push**.
3. VS Code will ask if you want to publish your branch — click **Yes**.

#### Terminal Method

```bash
git push -u origin your-branch-name
```

---

### 🔄 Part 6: Open a Pull Request (PR)

1. Go to your repo on GitHub (via browser).
2. You’ll see a “Compare & pull request” banner — click it.
3. Fill in a short title and description of your changes.
4. Click **Create pull request**.

---

### 👀 Part 7: Review and Merge

- Discuss and review PRs with teammates.
- If there are no conflicts, click **Merge pull request** on GitHub.
- After merging, delete your branch (optional but tidy).

---

### 🔄 Part 8: Pull Latest Changes

Before starting any new work, **always sync up** with your teammates!

#### GUI Method

1. Click on the **Source Control panel**.
2. Click the **three dots → Pull**.

#### Terminal Method

```bash
git checkout main
git pull origin main
```

---

## 🧠 Tips for Success

- **Branch for each task**: One branch per student or per change.
- **Pull before pushing**: Sync often!
- **Commit messages**: Be clear and descriptive.
- **Check GitHub often**: Review teammates’ pull requests.

---

## ⚠️ Common Issues & Fixes

| Issue                       | Fix                                                        |
|----------------------------|-------------------------------------------------------------|
| Accidentally edited `main` | Create a branch, then stash or copy changes                |
| Merge conflict              | Use VS Code’s merge editor or ask a teammate for help       |
| Can't push branch           | Run `git push -u origin branch-name` the first time         |
| Forgot to pull first        | Pull, then re-apply or rebase your changes                  |

---

Happy collaborating! 🚀
