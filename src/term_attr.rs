use crossterm::terminal::size;

fn get_term_dim() -> (u16, u16) {
    let (cols, rows) = size().unwrap();
    println!("{} {}", cols, rows);
    return (rows, cols);
}
