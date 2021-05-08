use owo_colors::OwoColorize;
use std::fmt::{Display, Error, Formatter};

pub enum Num {
    Int(i32),
    Float(f64),
    Text(String),
    NA(String),
}

//pub struct Pillar(pub Vec<Vec<String>>);
//impl Display for Pillar{
//    fn fmt(&self, f: &mut Formatter) -> Result<(), Error> {
//    }
//}

pub struct StringType(pub Vec<String>);
impl Display for StringType {
    fn fmt(&self, f: &mut Formatter) -> Result<(), Error> {
        println!("{}", "<pillar>".truecolor(129, 161, 193).bold().dimmed());
        println!("{}", "<char>".truecolor(129, 161, 193).bold().dimmed());
        //let mut comma_separated = String::new();
        let mut comma_separated = String::new();
        for num in &self.0[0..self.0.len()] {
            //let v = format_if_na(&num).to_string();
            comma_separated.push_str(&num.to_string());
            comma_separated.push_str("\n");
            //if is_na(&v) == true{
            //    return writeln!(f, "{}", v.truecolor(180,142,173));
            //}else{
            //    return writeln!(f, "{}", v.truecolor(143,188,187));
            //}
        }
        // this line is just to prevent fn fmt from throwing an error
        comma_separated.push_str(&self.0[self.0.len() - 1].to_string());
        //writeln!(f, "<pillar>\n<int>\n{}\n", comma_separated);
        write!(f, "{:>}", comma_separated)
    }
}
