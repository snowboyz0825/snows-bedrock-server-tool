#if you're stripped down enough not to have python, that's on you.
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python is not installed. Please install it to run this script."
    exit 1
fi

if ! command -v java >/dev/null 2>&1; then
    read -p "java, a dependancy, is not installed. Would you like to install it now? (y/n) " answer
    case "$answer" in
        [Yy]* )
             sudo apt-get install -y default-jdk
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

if ! command -v restic >/dev/null 2>&1; then
    read -p "restic, a dependancy, is not installed. Would you like to install it now? (y/n) " answer
    case "$answer" in
        [Yy]* )
             sudo apt-get install -y restic
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

if ! command -v unzip >/dev/null 2>&1; then
    read -p "unzip, a dependancy, is not installed. Would you like to install it now? (y/n) " answer
    case "$answer" in
        [Yy]* )
             sudo apt-get install -y unzip
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

sudo apt install -y python3-pip
pip install -U discord.py --break-system-packages 

wget https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.26.40.8.zip -O bedrock-server.zip

echo "unzipping bedrock server..."
unzip -q bedrock-server.zip -d bedrock-server
chmod +x bedrock-server/bedrock_server

rm bedrock-server.zip

mkdir joinbot

wget https://github.com/MCXboxBroadcast/Broadcaster/releases/download/149/MCXboxBroadcastStandalone.jar -P joinbot

touch bedrock-server/server.log

sed -i 's/allow-list=true/allow-list=false/g' bedrock-server/server.properties

tmux new -d -s mcserver

tmux send-keys -t mcserver "cd bedrock-server" enter "chmod +x bedrock_server" enter "./bedrock_server 2>&1 | tee -a server.log" enter