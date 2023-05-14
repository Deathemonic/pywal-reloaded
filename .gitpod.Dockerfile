ARG ARCH=amd64
FROM samip537/archlinux:$ARCH

RUN pacman -Sy --noconfirm --needed base-devel

RUN rm /var/lib/pacman/sync/*

RUN pacman -Sy go git --noconfirm

RUN groupadd wheel && groupadd users
RUN useradd -G wheel -m user
RUN echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN chown -R user:wheel /usr/local/src/

USER user
WORKDIR /usr/local/src/

RUN git clone https://aur.archlinux.org/yay.git
RUN cd yay && makepkg -si --noconfirm
RUN sudo rm -f \
      /var/cache/pacman/pkg/* \
      /var/lib/pacman/sync/* \
      /README \
      /etc/pacman.d/mirrorlist.pacnew
