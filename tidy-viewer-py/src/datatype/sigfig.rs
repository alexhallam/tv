use core::str;

// The general logic and return values in this file were learned from the GNU R package pillar in the sigfig.R file.
// A special thanks to the great code quality from Hadley Wickham, Jim Hester, and krlmlr
//
// Format numbers in decimal notation
//
// This formatting system is designed to make it as easy as possible to
// compare columns of numbers.
//
// DecimalSplitsList
//  val: f64, - the given float
//  sigfig: i64, - the given sigfigs (default of 3)
//  neg: bool, - Is a negative needed
//  lhs: String, - Left-hand-side of decimal string
//  rhs: f64, - Right-hand-side budget after spending the lhs digits
//  dec: bool, - should the decimal be included in the print
//
//
//
//                                                                lhs == 0.0
//                                   True                            │                            False            100.0
//                    0.001        ┌─────────────────────────────────┴──────────────────────────────────┐          123.450
//                   -0.12345      │                                                                    │          123456.0
//                   -0.01         │                                                       1 +log10(lhs) >= sigfig
//                                 │                          True                                      │               False
//          n = ((floor(log10(abs(x))) + 1 - sigfig)          ┌─────────────────────────────────────────┴────────────────────┐
//          r =(10^n) * round(x / (10^n))                     │                                                              │
//          return r                                     rhs > 0.0                                                     has negative
//                                 True                       │          False                       True                    │              False
//                                 ┌──────────────────────────┴───────────────┐                         ┌────────────────────┴──────────────┐
//                                 │                                          │                         │                                   │
//                           has negative                                 has negative               concatonate:                     concatonate:
//                                 │                                          │                      (-)                              (lhs)
//                     ┌───────────┴─────────────┐                 ┌──────────┴─────────┐            (lhs)                            (point)
//                     │                         │                 │                    │            (point)                          + sigfig - log10(lhs) from rhs
//                     │                         │                                                   + sigfig - log10(lhs) from rhs
//                     │                         │              concatonate:    concatonate:         (-12.345 -> -12.3)               (12.345 ->  12.3)
//                     │                         │              (-)             (lhs)                (-1.1 -> -1.10)                  (1.1 -> 1.10)
//                     │                         │              (lhs)
//                     │                         │                              (1234.0 -> 1234)
//                                                         (-1234.0 -> -1234)
//            concatonate:           concatonate:
//            (-)                    (lhs)
//            (lhs)                  (point)
//            (point)
//            (-123.45 -> -123.)   (1234.50 -> 1234.)
//
//

pub struct DecimalSplits {
    pub val: f64,
    pub sigfig: i64,
}

impl DecimalSplits {
    pub fn value(&self) -> f64 {
        self.val
    }
    pub fn sig_fig(&self) -> i64 {
        self.sigfig
    }
    pub fn neg(&self) -> bool {
        is_neg(self.val)
    }
    pub fn lhs(&self) -> f64 {
        get_lhs(self.val)
    }
    pub fn rhs(&self) -> f64 {
        get_rhs(self.val)
    }
    //pub fn dec(&self) -> bool {
    //    is_decimal(self.val)
    //}
    pub fn final_string(&self) -> String {
        get_final_string(
            self.value(),
            self.lhs(),
            self.rhs(),
            self.neg(),
            self.sig_fig(),
        )
    }
}

fn is_neg(x: f64) -> bool {
    x < 0.0
}

fn get_lhs(x: f64) -> f64 {
    x.trunc().abs()
}

fn get_rhs(x: f64) -> f64 {
    let xint = x.trunc();
    let frac = x - xint;
    frac.abs()
    //let s = format!("{:.12}", frac.abs()); //The 10 is arbitraty, but this condition puts a cap on sigfig size
    //let f: f64 = s.parse::<f64>().unwrap();
    //f
}

//fn is_decimal(x: f64) -> bool {
//    let r: f64 = x.trunc() as f64;
//    let l = x / r;
//    l > 1.0
//}

pub fn get_final_string(x: f64, lhs: f64, rhs: f64, neg: bool, sigfig: i64) -> String {
    if lhs.abs() + rhs.abs() == 0.0 {
        "0".to_string()
    } else if lhs == 0.0 {
        //n = ((floor(log10(abs(x))) + 1 - sigfig)
        //r =(10^n) * round(x / (10^n))
        let n = x.abs().log10().floor() + 1.0 - sigfig as f64;
        let r: f64 = 10f64.powf(n) * ((x / 10f64.powf(n)).round());
        let tmp_string = r.to_string();
        if tmp_string.len() > 13 {
            // 13 is arbitraty. There may be a more general solution here!
            // Problem: debug val: 0.0001 => final_string: "0.00009999999999999999"
            let j = (x.abs().log10().floor()).abs() as usize;
            if j >= sigfig as usize {
                // long tail sigfigs
                // 0.0001
                // 0.001
                let w = (x.abs().log10().floor()).abs() as usize;
                let fstring = format!("{r:.w$}");
                fstring
            } else {
                // standard lhs only sigs
                //-0.9527948462413667 -> -0.953
                let fstring = format!("{:.w$}", r, w = (sigfig as usize));
                fstring
            }
        } else {
            //println!("{:?}", tmp_string);
            tmp_string
        }
    } else if lhs.log10() + 1.0 >= sigfig as f64 {
        if rhs > 0.0 {
            let total = lhs + rhs;
            let total_string = total.to_string();
            let total_clone = total_string.clone();
            let split = total_clone.split('.');
            let vec: Vec<&str> = split.collect();
            let len_to_take = vec[0].len() + 1; // lhs + point
            if neg {
                //concatonate:
                //(-)
                //(lhs)
                //(point)
                //(-123.45 -> -123.)
                let pos_string = (total_string[..len_to_take]).to_string();
                let neg_string = "-".to_string();
                [neg_string, pos_string].join("")
            } else {
                //concatonate:
                //(lhs)
                //(point)
                //(123.45 -> 123.)
                total_string[..len_to_take].to_string()
            }
        } else if neg {
            //concatonate:
            //(-)
            //(lhs)
            //(-1234.0 -> -1234)
            let total = lhs + rhs;
            let total_string = total.to_string();
            let total_clone = total_string.clone();
            let split = total_clone.split('.');
            let vec: Vec<&str> = split.collect();
            let len_to_take = vec[0].len(); // lhs
            let pos_string = (total_string[..len_to_take]).to_string();
            let neg_string = "-".to_string();
            [neg_string, pos_string].join("")
        } else {
            //concatonate:
            //(lhs)
            //(1234.0 -> 1234)
            //(100.0 -> 100)
            //let total = lhs + rhs;
            //let total_string = total.to_string();
            let total_string = x.to_string();
            let total_clone = total_string.clone();
            let split = total_clone.split('.');
            let vec: Vec<&str> = split.collect();
            let len_to_take = vec[0].len(); // lhs
            total_string[..len_to_take].to_string()
        }
    } else if rhs == 0.0 {
        //concatonate:
        //(lhs)
        //(point)
        //+ sigfig - log10(lhs) from rhs
        let total_string = x.to_string();
        let total_clone = total_string.clone();
        let split = total_clone.split('.');
        let vec: Vec<&str> = split.collect();
        let len_to_take_lhs = vec[0].len(); // point -> +1 to sigfig
        total_string[..len_to_take_lhs].to_string()
    } else if neg {
        //concatonate:
        //(-)
        //(lhs)
        //(point)
        //+ sigfig - log10(lhs) from rhs
        //(-12.345 -> -12.3)
        //(-1.2345 -> -1.23)
        // need a rhs arguments here
        //let total = lhs + rhs;
        //let total_string = total.to_string();
        let w: usize = (sigfig as usize) - 1;
        let x = format!("{x:.w$}");
        let total_string = x;
        let total_clone = total_string.clone();
        let split = total_clone.split('.');
        let vec: Vec<&str> = split.collect();
        let len_to_take_lhs = vec[0].len(); // point -> +1 to sigfig
                                            // The plus one at the end stands for the '.' character as lhs doesn't include it
        let len_to_take_rhs = std::cmp::min((sigfig as usize) - len_to_take_lhs, vec[1].len()) + 1;
        let len_to_take = len_to_take_lhs + len_to_take_rhs + 1;
        //println!("x: {:?}", x);
        total_string[..len_to_take].to_string()
    } else {
        //concatonate:
        //(lhs)
        //(point)
        //+ sigfig - log10(lhs) from rhs
        //(12.345 -> 12.3)
        //(1.2345 -> 1.23)
        // need a rhs arguments here
        //let total = lhs + rhs;
        //let total_string = total.to_string();
        let w: usize = (sigfig as usize) - 1;
        let x = format!("{x:.w$}");
        let total_string = x;
        let total_clone = total_string.clone();
        let split = total_clone.split('.');
        let vec: Vec<&str> = split.collect();
        let len_to_take_lhs = vec[0].len(); // point -> +1 to sigfig
        let len_to_take_rhs = ((sigfig + 1) as usize) - len_to_take_lhs;
        let len_to_take = len_to_take_lhs + len_to_take_rhs;

        if len_to_take >= total_string.len() {
            total_string
        } else {
            total_string[..len_to_take].to_string()
        }
    }
}
