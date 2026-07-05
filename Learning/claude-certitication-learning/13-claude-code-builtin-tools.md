# Chapter 13: Claude Code Built-in Tools

---

## 13.1 Tool Selection Reference

| Task | Tool | Example |
|------|------|---------|
| Find files by name/pattern | **Glob** | `**/*.test.tsx`, `src/components/**/*.ts` |
| Search within files | **Grep** | Function name, error message, import |
| Read a file in full | **Read** | Load file for analysis |
| Write a new file | **Write** | Create file from scratch |
| Edit existing file precisely | **Edit** | Replace specific snippet via unique text match |
| Run shell command | **Bash** | git, npm, run tests, build |

### Key Distinctions
- **Glob** = find files by **name/extension patterns**
- **Grep** = search **within file contents** (function names, errors, imports)
- **Read/Write** = full-file operations
- **Edit** = precise changes via unique text matches

---

## 13.2 Incremental Investigation Strategy

Do **not** read all files at once. Build understanding incrementally:

```text
1. Grep: find entry points (function definition, export)
2. Read: read the found files
3. Grep: find usages (import, calls)
4. Read: read consumer files
5. Repeat until complete picture
```

---

## 13.3 Fallback: Read + Write Instead of Edit

When Edit fails due to non-unique text match:

```text
1. Read — load full file content
2. Modify content programmatically
3. Write — write updated version
```

---

## Agent SDK Built-in Tools (Extended)

Beyond Claude Code CLI, the Agent SDK also includes:

| Tool | Purpose |
|------|---------|
| WebSearch | Search web for current information |
| WebFetch | Fetch and parse web page content |
| AskUserQuestion | Ask clarifying questions with multiple choice |
| Monitor | Watch background script, react to each output line |

---

## Memory Aids

| Need | Tool |
|------|------|
| "Find all test files" | Glob |
| "Where is function X defined?" | Grep |
| "Read this file" | Read |
| "Create new file" | Write |
| "Change one line" | Edit (or Read+Write if non-unique) |
| "Run tests" | Bash |
