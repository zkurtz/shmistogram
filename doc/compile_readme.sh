cp readme_preamble.md ../README.md
sed -e 's|(demo|(demo\/demo|g' ../demo/demo.md >> ../README.md
cat readme_details.md >> ../README.md
