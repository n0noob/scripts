#!/usr/bin/env bash

##################################################
# Use this script for setting up git             #
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

git config --global user.name "$user"
git config --global user.email "$email"
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'

# Generate ssh key
echo "Generating ssh key for git...please press enter to all prompts"
ssh-keygen -t ed25519 -C "$email"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
echo "#######################################################################"
cat ~/.ssh/id_ed25519.pub
echo "#######################################################################"
echo "Copy the above ssh key and add it to your git account"

echo "git config --global --list"

git config --global --list
