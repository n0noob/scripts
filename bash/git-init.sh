#!/usr/bin/env bash

##################################################
# Use this script for adding git user and email  #
##################################################

pacman -Qi git >/dev/null 2>&1

if [ $? -ne 0 ]; then
	echo "git is not installed in this system. Installing now..."
	sudo pacman -S git
fi

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
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'

echo "git config --global --list"

git config --global --list

