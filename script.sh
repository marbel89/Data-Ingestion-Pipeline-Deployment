#!/bin/bash

# Make sure, the Python.exe folder is part of your environmental path variables

echo "Start cleaning data? [y/n]"
read continue

if [ $continue == "y" ]
then
    echo "Start..."
    python dev/main.py
    echo "Done."

    dev_version=$(head -n1 dev/changelog.md)
    dev_version=$(head -n1 prod/changelog.md)

    read -a splitversion_dev <<< $dev_version
    read -a splitversion_prod <<< $prod_version

    dev_version=${splitversion_dev[1]}
    prod_version=${splitversion_prod[1]}

    if [ $prod_version != $dev_version ]
    then
        echo "Difference between prod and dev version! Move files to prod? [y/n]"
        read scriptcontinue
    else
        scriptcontinue="n"
    fi
else
    echo "Ending..."
fi

if [ $scriptcontinue == "y" ]
then
    for filename in dev/*
    do
        if [ $filename == "dev/main_cancelled_subscribers.csv" ] || [ $filename == "dev/changelog.md" ]
        then
            cp $filename prod
            echo "Copying into prod: " $filename
        else
            echo "Not copying into prod: " $filename
        fi
    done 
else
    echo "Aborting..."
fi

