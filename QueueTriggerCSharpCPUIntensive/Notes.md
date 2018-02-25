# Notes for commands

## Adding message to a queue, where message is base64 encoded

`az storage message put -q myqueue-items-2 --content "MTAwMDAwCg=="`
