#!/bin/sh

# Adapted from https://stackoverflow.com/questions/1964142/how-can-i-list-all-the-different-versions-of-a-file-and-diff-them-also/32941633
# Execute from the project's home directory

IN_DIR="assets/data"
OUT_DIR="timelapse/data"
DATE_FNAME="report_date.csv"
DB_FNAME="db_scraped.csv"
DB_FNAME="db_countries.csv"

DATE_PATH="$IN_DIR/$DATE_FNAME"
DB_PATH="$IN_DIR/$DB_FNAME"

index=1
for commit in $(git log --pretty=format:%h "$DB_PATH")
do
  padindex=$(printf %03d "$index")
  out_dir_ver="$OUT_DIR/_$padindex-$commit"
  mkdir $out_dir_ver
  out_db="$out_dir_ver/$DB_FNAME"
  out_date="$out_dir_ver/$DATE_FNAME"
  log="$out_dir_ver/logmsg.txt"
  echo "saving version $index to dir $out_dir_ver for commit $commit"
  echo "*******************************************************" > "$log"
  git log -1 --pretty=format:"%s%nAuthored by %an at %ai%n%n%b%n" "$commit" >> "$log"
  echo "*******************************************************" >> "$log"
  #git show "$commit:./$DATE_PATH" > "$out_date"
  git show "$commit:./$DB_PATH" > "$out_db"
  let index++
done
