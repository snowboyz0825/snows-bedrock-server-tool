if ! command -v java >/dev/null 2>&1; then
    echo "Java is not installed. Please install it to run this script."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python is not installed. Please install it to run this script."
    exit 1
fi

if ! command -v tmux >/dev/null 2>&1; then
    read -p "tmux, a dependancy, is not installed. Would you like to install it now? (y/n) " answer
    case "$answer" in
        [Yy]* )
             sudo apt-get install -y tmux
            ;;
        [Nn]* )
            echo "Aborted."
            exit 1
            ;;
        * )
            exit 1
            ;;
    esac
fi

wget https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.26.40.8.zip -O bedrock-server.zip

echo "unzipping bedrock server..."
unzip -q bedrock-server.zip -d bedrock-server
chmod +x bedrock-server/bedrock_server

rm bedrock-server.zip

mkdir joinbot

wget https://github.com/MCXboxBroadcast/Broadcaster/releases/download/149/MCXboxBroadcastStandalone.jar -P joinbot

