path="./logid/"


url_prefix="https://tenhou.net/5/mjlog2json.cgi?"

# mjlog_url2json "2024120321gm-00a9-0000-7b9af3aa"

cd $path || exit
mkdir ../log_json/

ls *txt | while read line
do

    while read -r id
    do
        counter=0
        curl $url_prefix$id>../log_json/$id.json
    done <$line
done
