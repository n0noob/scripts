#!/usr/bin/env bash

##################################################
# Use this script for adding user name and email #
##################################################

read -p "Enter your git user name here: " user

if [ -z "$user" ]
then
      echo "Invalid user name entered"
      exit 1
fi

read -p "Enter your registered email here: " email

if [ -z "$email" ]
then
      echo "Invalid email entered"
      exit 1;
fi

echo "Setting user  : >$user<"
echo "Setting email : >$email<"

git config --global user.name "\"$user\""
git config --global user.email "\"$email\""

echo "git config --global --list"

git config --global --list
