# Contributing

This page tells you how to add or change a figure, from the first idea to the merge.
You do not need to know git well.
Each step gives the commands to type.

For the content of a figure folder, read [figures/README.md](figures/README.md).

## Before you start

You need:

- A GitHub account with access to [marsico-lab/parnet--paper](https://github.com/marsico-lab/parnet--paper).
- `git` and [pixi](https://pixi.sh) on your computer.
- Optional: the GitHub command line tool `gh` (`pixi global install gh`).
  Every `gh` command below also has a button on the GitHub website.

Do these steps one time only:

```sh
git clone https://github.com/marsico-lab/parnet--paper.git
cd parnet--paper
git switch dev
pixi install                  # installs the environment (a few minutes)
pixi run install-kernel       # optional: notebook kernel "parnet--paper" for VS Code
pixi run install-hooks        # optional: checks run each time you commit
pixi run figure _example      # builds the example figure; it must end with "OK"
```

## Branches

| Branch          | Content                                                   | Who writes to it                            |
| --------------- | --------------------------------------------------------- | ------------------------------------------- |
| `main`          | The version of the paper that was submitted or published. | Maintainer only, at milestones.             |
| `dev`           | All finished figures, the tools and this documentation.   | Nobody directly. Only merged pull requests. |
| `figure/<name>` | One figure while it is in progress.                       | The person who works on that figure.        |

The branch name matches the folder name: branch `figure/main-mutations` changes folder `figures/main_mutations/`.

## The procedure in short

1. Open an issue that describes the figure.
1. Create a branch from `dev`.
1. Open a draft pull request.
1. Work on the figure and push your commits.
1. Ask for a review.
1. Co-authors review and approve.
1. Merge into `dev`.

The sections below give the details of each step.

## 1. Open an issue

An issue tells the co-authors that you work on a figure.
It is also the place to discuss what the figure shows.

1. On GitHub, go to **Issues**, then click **New issue**.
1. Select the template **Figure**.
1. Fill in the title, the panels, the data and the reviewers.
1. Click **Create**.

With `gh`: `gh issue create --template figure.md`.

Note the issue number (for example `#12`).
You use it in step 3.

## 2. Create a branch

Start from an up-to-date `dev`:

```sh
git switch dev
git pull
git switch -c figure/main-mutations
```

Then create the figure folder from the example (see [figures/README.md](figures/README.md#start-a-new-figure)), and make a first commit:

```sh
git add figures/main_mutations
git commit -m "Start figure main_mutations"
git push -u origin figure/main-mutations
```

## 3. Open a draft pull request

A draft pull request (PR) shows your progress to the co-authors.
Nobody can merge a draft by accident.

1. On GitHub, click **Compare & pull request** on the yellow banner.
1. Set **base** to `dev`.
   Do not use `main`.
1. Keep the text of the template.
   Write `Closes #12` (your issue number) on the first line.
1. Click the arrow next to **Create pull request**, then click **Create draft pull request**.

With `gh`: `gh pr create --draft --base dev`.

## 4. Work and show progress

Work on your branch only.
Before you start a work session, make sure that you are on your branch:

```sh
git branch --show-current        # must show figure/<name>
```

When a part of the figure works:

```sh
pixi run figure main_mutations   # rebuild; it must end with "OK"
git add figures/main_mutations
git commit -m "Add panel B heatmap"
git push
```

Each push updates the pull request.
The **Files changed** tab shows the new `preview.png` next to the old one.

To show a step to the co-authors, write a comment in the pull request.
Drag `figures/<name>/preview.png` into the comment box to attach the image.

### Get the latest changes from `dev`

Other figures are merged into `dev` while you work.
To get their changes (for example a new shared color):

```sh
git switch dev
git pull
git switch figure/main-mutations
git merge dev
git push
```

If git reports a conflict, ask the maintainer for help.
Do not delete the branch.

### Changes outside your figure folder

Some changes affect all figures: `figures/style.yaml`, `data/`, `parnet_paper/`, `pixi.toml`.
Put each of these changes in a separate commit.
Describe it in the pull request, so that the reviewers see it.

## 5. Ask for a review

Do these checks first:

```sh
pixi run figure main_mutations   # must end with "OK"
pixi run check-all               # must show no "Failed"
```

Then:

1. In the pull request, click **Ready for review**.
1. On the right, under **Reviewers**, add the co-authors listed in the issue.

With `gh`: `gh pr ready`, then `gh pr edit --add-reviewer <github-name>`.

## 6. Review (for co-authors)

You receive an email or a GitHub notification.
Open the pull request.

1. Look at the figure: open **Files changed**, then find `preview.png`.
   GitHub shows the old and the new image.
   Select **2-up**, **Swipe** or **Onion skin** to compare them.
1. To comment on one line, move the mouse over the line and click **+**.
1. To propose a change to one line of text or code, click **+**, then the **suggestion** button (the ± icon).
   The author can accept your suggestion with one click.
1. For a general comment on the figure, write in the **Conversation** tab.
1. When you are done, click **Review changes** (top right of **Files changed**) and select one option:
   - **Comment**: you have questions, but no decision yet.
   - **Request changes**: the figure must change before the merge.
   - **Approve**: the figure is ready.

The author answers each comment.
When a comment is solved, the author clicks **Resolve conversation**.
If the author changes the figure after your approval, look at it again.

## 7. Merge into `dev`

The author merges when all these conditions are true:

- All reviewers listed in the issue approved.
- No review says **Request changes**.
- All conversations are resolved.
- `pixi run figure <name>` ends with `OK`.

To merge:

1. At the bottom of the pull request, select **Create a merge commit**.
   Do not select **Squash** or **Rebase**.
1. Click **Merge pull request**, then **Confirm merge**.
1. Click **Delete branch**.

The issue closes automatically, because the pull request contains `Closes #12`.

On your computer:

```sh
git switch dev
git pull
git branch -d figure/main-mutations
```

If the co-authors do not agree, discuss in the pull request.
The maintainer makes the final decision.

## Rules

- Do not commit on `dev` or `main`.
- One branch and one pull request for each figure.
- Do not recompute an analysis in this repository.
  Copy the result tables from the analysis repository, and write their origin in a `README.md` next to them.
- Commit the outputs (`panels/`, `preview.*`, `<name>.tex`) after each rebuild, and `<name>-figure.tex` when you change it.
  The reviewers see the figure through them.
- Write Markdown with one sentence per line.

## Checks

```sh
pixi run check-all      # all checks on all files
pixi run format         # format the Python code
```

The checks are: ruff (Python), snakefmt (Snakemake), markdownlint and mdformat (Markdown), typos (spelling), editorconfig-checker, taplo (TOML), yamllint (YAML).
If typos reports a correct scientific word, add it to `_typos.toml`.

## Releases (maintainer)

At a milestone (submission, revision), merge `dev` into `main` with a pull request, then add a tag:

```sh
git switch main
git pull
git tag -a submission-1 -m "First submission"
git push origin submission-1
```
