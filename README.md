kaban
=====

A git-based todo manager for personal goals, tasks and projects.

Keep your todos sound and synced! Organize and track your tasks with ease!

You tend to spend the bulk of your time in the command line, right? One day you
suddenly remember that odd job you promised you would do for your landlady, you
might as well add it to that sprawling TODO spreadsheet you've got...
somewhere...

The boss calls you about an urgent hotfix you need to deliver by yesterday, this
*has* to go in that super important txt right about now... where did you put it
again?

You know that amazing new feature request a coworker came up with for your pet
project years ago that you're 100% sure you had written on that one post-it you
might have eatan at some point in lieu of breakfast? That's not coming back,
unless you look them up on MySpace or something. Oh noes!

The next day you're on a plane to Hong Kong with no Internet access, I mean the
plane, not Hong Kong. You've got several hours to get some work done... except
it turns out you left your TODO list in Google Keep. D'oh!

Fear not, `kaban`'s got you covered!

## What can `kaban` do for me?

Basically it lets you stay atop your ever-changing pile of tasks, todos and
challenges without worrying about misplacing your post-its or TODO.txt file:
`kaban` takes that right off your plate for you by storing your task data and
history in a GitHub repository. Your tasks and progress will be kept in a place
you can't lose or forget, synced via `git` across all machines where `kaban`
is installed. That's 4 to 5 percent of mental energy saved for **you** that you
can spend on accomplishing your goals quicker!

You can also use `kaban` to track the hours and days you invest in your numerous
tasks and projects. Want a detailed picture of how much time different kinds of
tasks tend to take versus your initial estimates, statistically speaking?
`kaban`'s up to the task, right down to a task.

## What's with the funky name?

"`kaban`" is Japanese for bag(s) or suitcase(s), as in bags of rainbow and
suitcases of delight. *'n* it's also missing an 'n' from the popular workplace
process management methodology known as Kanban -- also from Japan, incidentally.

## Why use `git` to keep track of your todos?

I mean why put whipped cream on your pancakes? Because it's awesome, that's why.
`git` is a highly reliable version control system with great performance -- like
keeping your stuff in a secure vault you've got a direct highway to. `git`
guarantees the integrity of your repository, and stores the history of changes
forever.

`kaban` records every task and every change you make to a task in separate `git`
commits under the hood. This way your `kaban` command history builds up a
corresponding chain of `git` commits.

## Wait, isn't that kind of wasteful?

I mean kind of, but `git` objects are compressed by default and you have tons of
disk space anyway, you might want to waste it on something useful. It lets you
check your history at any time, diff commits to see how far you have come etc.

Also, if `kaban` happens to be unavailable on a system you find yourself using
(such as a borrowed laptop) you won't need to crack some arcane binary format
to do a simple undo or an update, for example -- you can just fall back on
the same raw `git` commands that `kaban` would run for you.

## So what's keeping me from editing a custom yaml file manually and committing it every time instead of using kaban?

Literally nothing, really. Congratulations, you gamed the system.

## How mature is `kaban`'s featureset? How stable is the application?

`kaban` is currently in early alpha, so using it is like playing a text
adventure against a computer that's clinically insane right about now.

Major breaking changes are to be expected literally any day or more like any
minute, but if you check back once a week or so, sooner or later you might find
something you'll find interesting here -- and perhaps enjoy using eventually.

## How can I contribute?

I'm glad you asked! If you feel like improving `kaban`, fixing bugs, or turning
it into a full-fledged death star, head on over to
[the official GitHub repo](https://github.com/nilthehuman/kaban) where pull
requests are more than welcome.

