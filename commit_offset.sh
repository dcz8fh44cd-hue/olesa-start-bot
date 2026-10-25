git config user.email bot@users.noreply.github.com
git config user.name start-bot
git add offset.txt
git commit -m "offset" || true
git push origin HEAD:main || true
