# ParliamentBomb

Simple No-Compromise Discord bot written in Rust.

## Features

- Logging
- Weekly status report (TBA)
- Moderation
- Easy-to-use 
- Simple Configuration
- Community Interaction Support (voting, polls, etc.)

## Compiling ParliamentBomb
There are many ways to compile ParliamentBomb.

### Nix (with `nix build`) (recommended)
The recommended way to compile & develop ParliamentBomb is with Nix. This ensures you have all of the build dependencies. **You must have the Nix Package manager installed.**

1. Clone Parliamentbomb
   
   ```git clone github.com/gradetools/ParliamentBomb```

2. Run this command

    ```nix build --extra-experimental-features nix-command --extra-experimental-features flakes```
   
3. The binary should be located in `/nix/store`. Run the binary with `./result/bin/parliamentbomb`

### Nix (with `nix develop`) 
You may also manually build with cargo, while using the Nix developer shell

1. Clone Parliamentbomb
   
   ```git clone github.com/gradetools/ParliamentBomb```

2. Enter the developer shell by running this command:

    ```nix develop --extra-experimental-features nix-command --extra-experimental-features flakes```
   
3. The build dependencies should be installed, so you can begin compiling with `cargo build`


### Manual Compile 
If you are unable to use Nix, you may manually compile with Cargo.


#### Build Dependencies
The dependencies required for compiling Parliamentbomb are:

```
cargo
rust
pkg-config
openssl
```

1. Clone Parliamentbomb
   
   ```git clone github.com/gradetools/ParliamentBomb```

2. Ensure you have the proper versions of the dependencies installed. This may vary between distros.

3. Compile Parliamentbomb
   ```cargo build```
