use regex::Regex;


fn main() {

    fn trunc_strings(vec_col: Vec<&str>, width: usize) -> Vec<String>{
        let ellipsis = '\u{2026}'.to_string();
        let v = vec_col
        .into_iter()
        .map(String::from)
        .map(|mut string| 
             if string.len() > width { string.truncate(width); [string, ellipsis.to_string()].join("") } 
             else {string.truncate(width); string})
        .map(|string| format_if_na(&string))
        .collect::<Vec<String>>();
        return v
    }
    fn is_na(text: &String) -> bool{
        //grex NA Null na null "" None Na N/A NaN NAN nan
        let rgex = r"^$|^(?:N(?:(?:(?:one|AN|a[Nn]|/A)|[Aa])|ull)|n(?:ull|an?)|(?:missing))$";
        let r = Regex::new(rgex).unwrap();
        let lgl = r.is_match(&text);
        return lgl
    }
    fn format_if_na(text: &String) -> String{
        let s = is_na(&text);
        let missing_string_value: String = "NA".to_string();
        let string: String = if s == true { missing_string_value } else {text.to_string()};
        return string
    }
    fn float_has_point(text: &String)-> bool{
        let lgl: bool = text.contains(".");
        return lgl
    }
    fn get_decimal_len(text: &String) -> usize{
        // if number is 1 as oppose to 1.0 then return 0
        let width: usize= if float_has_point(text) == true {text.split(".").collect::<Vec<&str>>()[1].len()+1} else{0};
        return width 
    }
    fn get_left_decimal_len(text: &String) -> usize{
        // gets len of whole numbers to the left of the decimal
        // if number is 1 as oppose to 1.0 then return 0
        let width: usize= if float_has_point(text) == true {text.split(".").collect::<Vec<&str>>()[0].len()} else{text.len()};
        return width 
    }
    fn float_pad(text: &String, max_width: usize) -> String{
        let width = get_decimal_len(&text);
        let whole_number_width = get_left_decimal_len(&text);
        //todo pass width as arg
        //let width_to_append: usize = (max_width + width + whole_number_width + 1) - width;
        let width_to_append: usize = (max_width + width + whole_number_width) - whole_number_width - 1;
        //let width_to_append: usize = width + whole_number_width + max_width;
        let f = format!("{:>width$}", text, width = width_to_append).to_string();
        return f
    }
    fn float_format(text: &String, max_width: usize) -> String{
        let is_na = is_na(&text);
        let string: String = if is_na == true {format_if_na(text)} else {float_pad(text, max_width)};
        return string;
    }

    let a = vec!["abc","abcde","abcdefgh","abcdefghijkl","","","abcdefghijklmnop"];
    let b = vec!["0.0001","0.001","0.01","0.1","1","","100"];

    //split by decimal and count the largest decimal part 
    let vec_len = b.clone()
        .into_iter()
        .map(String::from)
        .map(|string| get_decimal_len(&string))
        .collect::<Vec<usize>>();
    // to do learn how to convert this &usize to usize
    let max_len = vec_len.iter().max().unwrap();

    let chr = trunc_strings(a.clone(), 6);
    let dbl = b.clone()
        .into_iter()
        .map(String::from)
        .map(|string| float_format(&string, 4))
        .collect::<Vec<String>>();

    println!("original chars: {:?}",a.clone());
    println!("original doubles: {:?}",b);

   let vs = tv::StringType(dbl);
   let vf = tv::StringType(chr);
   println!("{:^}\n{:^}", vs, vf);

}
