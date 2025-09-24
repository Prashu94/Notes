brew services start postgresql@15
brew services stop postgresql@15
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
/Volumes/MyPassport
mv ~/.ollama /Volumes/MyPassport/.ollama
ln -s /Volumes/MyPassport/.ollama ~/.ollama
export OLLAMA_HOME=/Volumes/MyPassport/.ollama
source ~/.zshrc
ollama run llama2
ollama stop llama2
