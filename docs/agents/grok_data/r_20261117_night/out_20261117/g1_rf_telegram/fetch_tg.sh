while read n; do
  [ -s "tg_html/$n.html" ] && continue
  curl -s -L -A "Mozilla/5.0 (X11; Linux x86_64)" --max-time 25 -o "tg_html/$n.html" -w "$n %{http_code} %{size_download} %{url_effective}\n" "https://t.me/s/$n"
  sleep 1.2
done < channel_list.txt
