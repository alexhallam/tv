# Maintainer: alexhallam <alexhallam6.28@gmail.com>
#
# This PKGBUILD was generated by `cargo aur`: https://crates.io/crates/cargo-aur

pkgname=tidy-viewer-bin
pkgver=0.0.11
pkgrel=1
pkgdesc="Head, but for csvs and with color"
url="https://github.com/alexhallam/tv"
license=("Unlicense/MIT")
arch=("x86_64")
provides=("tidy-viewer")
conflicts=("tidy-viewer")
source=("https://github.com/alexhallam/tv/releases/download/v$pkgver/tidy-viewer-$pkgver-x86_64.tar.gz")
sha256sums=("cf6459fbeee845f74b2a557730390e47d59b667b86548683f38539256640d9af")

package() {
    install -Dm755 tidy-viewer -t "$pkgdir/usr/bin"
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}