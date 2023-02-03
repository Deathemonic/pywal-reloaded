ARG ARCH=amd64
FROM lopsided/archlinux-$ARCH

RUN pacman -Syu --noconfirm --needed base-devel git neovim python-neovim neofetch ttf-jetbrains-mono python3 python-pip python-setuptools xdg-user-dirs zsh

# Remove current pacman database, likely outdated very soon
RUN rm /var/lib/pacman/sync/*
