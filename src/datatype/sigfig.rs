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
//                     │                         │              (-)             (lhs)
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
    pub fn dec(&self) -> bool {
        is_decimal(self.val)
    }
    pub fn final_string(&self) -> String {
        get_final_string(
            self.value(),
            self.lhs(),
            self.rhs(),
            self.neg(),
            self.sig_fig(),
        )
    }
    pub fn rhs_string_len(&self, string_final_string: String) -> usize {
        let split = string_final_string.split(".");
        let vec = split.collect::<Vec<&str>>();
        if vec.len() > 1 {
            let length = vec[1].len();
            length
        } else {
            0
        }
    }
    pub fn sigfig_index_lhs_or_rhs(&self) -> Option<bool> {
        sigfig_index_lhs_or_rhs(&self.final_string(), self.sig_fig())
    }
    pub fn sigfig_index_from(&self) -> Option<usize> {
        sigfig_index_from(&self.final_string(), self.sig_fig())
    }
    pub fn sigfig_index_to(&self) -> Option<usize> {
        sigfig_index_to(&self.final_string(), self.sig_fig())
    }
}

#[derive(Debug)]
pub struct DecimalSplitsList {
    pub val: f64,
    pub sigfig: i64,
    pub neg: bool,
    pub lhs: f64,
    pub rhs: f64,
    pub dec: bool,
    pub final_string: String,
    pub rhs_string_len: usize,
    pub sigfig_index_lhs_or_rhs: Option<bool>, // lhs => True; rhs => False
    pub sigfig_index_from: Option<usize>,
    pub sigfig_index_to: Option<usize>,
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

fn is_decimal(x: f64) -> bool {
    let r: f64 = x.trunc() as f64;
    let l = x / r;
    l > 1.0
}

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
            let w = (x.abs().log10().floor()).abs() as usize;
            let fstring = format!("{:.w$}", r, w = w);
            fstring
        } else {
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
        //(12.345 -> 12.3)
        //(1.2345 -> 1.23)
        // need a rhs arguments here
        //let total = lhs + rhs;
        //let total_string = total.to_string();
        let total_string = x.to_string();
        let total_clone = total_string.clone();
        let split = total_clone.split('.');
        let vec: Vec<&str> = split.collect();
        let len_to_take_lhs = vec[0].len(); // point -> +1 to sigfig
        let len_to_take_rhs = ((sigfig + 1) as usize) - len_to_take_lhs;
        if vec[1].len() > (sigfig - 2) as usize {
            let len_to_take = len_to_take_lhs + len_to_take_rhs + 1; // +1 for the space the neg sign takes
            total_string[..len_to_take].to_string()
        } else {
            let len_to_take = len_to_take_lhs + len_to_take_rhs;
            total_string[..len_to_take].to_string()
        }
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
        let total_string = x.to_string();
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

fn sigfig_index_lhs_or_rhs(final_string: &str, sigfig: i64) -> Option<bool> {
    // 123456 => {123}456
    // 0.00123 => 0.001{23}
    let split = final_string.split('.');
    let vec: Vec<&str> = split.collect(); // 12.345 -> ["12", "345"]
    let lhs = vec[0].len();
    if vec.len() > 1 {
        // if there is a decimal in the string
        let rhs = vec[1].len();
        if lhs > sigfig as usize {
            Some(true)
        } else if rhs > sigfig as usize {
            Some(false)
        } else {
            None
        }
    } else if lhs > sigfig as usize {
        Some(true)
    } else {
        None
    }
}

fn sigfig_index_from(final_string: &str, sigfig: i64) -> Option<usize> {
    // 123456 => {123}456
    // 0.00123 => 0.001{23}
    // split string on decimal
    // if lhs > sigfig => start = 0
    // else if rhs > sigfig => start = 3 // assuming sigfig = 3
    // else null
    let split = final_string.split('.');
    let vec: Vec<&str> = split.collect(); // 12.345 -> ["12", "345"]
    let lhs = vec[0].len();
    if vec.len() > 1 {
        // if there is a decimal in the string
        let rhs = vec[1].len();
        if lhs > sigfig as usize {
            Some(0)
        } else if rhs > sigfig as usize {
            Some(sigfig as usize)
        } else {
            None
        }
    } else if lhs > sigfig as usize {
        Some(0)
    } else {
        None
    }
}

fn sigfig_index_to(final_string: &str, sigfig: i64) -> Option<usize> {
    // 123456 => {123}456
    // 0.00123 => 0.001{23}
    // split string on decimal
    // if lhs > sigfig => end = lhs - sigfig
    // else if rhs > sigfig => end = lhs - sigfig // assuming sigfig = 3
    // else null
    let split = final_string.split('.');
    let vec: Vec<&str> = split.collect(); // 12.345 -> ["12", "345"]
    let lhs = vec[0].len();
    if vec.len() > 1 {
        // if there is a decimal in the string
        let rhs = vec[1].len();
        if lhs > sigfig as usize {
            let end = lhs - sigfig as usize;
            Some(end)
        } else if rhs > sigfig as usize {
            Some(rhs as usize)
        } else {
            None
        }
    } else if lhs > sigfig as usize {
        let end = lhs - sigfig as usize;
        Some(end)
    } else {
        None
    }
}

#[test]
fn test_f12345() {
    let f12345 = vec![12345.0, 1234.50, 123.45, 12.345, 1.2345, 0.12345, 0.0];
    let test_sigfig = vec![3, 3, 3, 3, 3, 3, 3];
    let test_neg = vec![false, false, false, false, false, false, false];
    let test_lhs = vec![12345.0, 1234.0, 123.0, 12.0, 1.0, 0.0, 0.0];
    let test_rhs = vec![
        0.0,
        0.5,
        0.45000000000000284,
        0.34500000000000064,
        0.23449999999999993,
        0.12345,
        0.0,
    ];
    let test_dec = vec![false, true, true, true, true, true, false];
    let test_final_string = vec!["12345", "1234.", "123.", "12.3", "1.23", "0.123", "0"];

    for i in 0..f12345.len() {
        let value = f12345[i];
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            rhs_string_len: x.rhs_string_len(x.final_string()),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, f12345[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
    }

    //    $sigfig
    //    [1] 3
    //    $num
    //    [1] TRUE TRUE TRUE TRUE TRUE TRUE
    //    $neg
    //    [1] FALSE FALSE FALSE FALSE FALSE FALSE
    //    $lhs
    //    [1] "12345" "1234"  "123"   "12"    "1"     "0"
    //    $lhs_zero
    //    [1] FALSE FALSE FALSE FALSE FALSE  TRUE
    //    $rhs
    //    [1] 0.000 0.000 0.000 0.300 0.230 0.123
    //    $rhs_digits
    //    [1]  0 -1  0  1  2  3
    //    $dec
    //    [1] FALSE  TRUE  TRUE  TRUE  TRUE  TRUE
    //    $exp
    //    [1] NA NA NA NA NA NA
    //    $si
    //    [1] FALSE
    //    attr(,"width")
    //    [1] 9
    //    12345
    //     1234.
    //      123.
    //       12.3
    //        1.23
    //        0.123
}

#[test]
fn test_f100() {
    let f100 = vec![100.0, 10.0, 1.0, 0.1, 0.01, 0.001, 0.0001];
    let test_sigfig = vec![3, 3, 3, 3, 3, 3, 3];
    let test_neg = vec![false, false, false, false, false, false, false];
    let test_lhs = vec![100.0, 10.0, 1.0, 0.0, 0.0, 0.0, 0.0];
    let test_rhs = vec![0.0, 0.0, 0.0, 0.1, 0.01, 0.001, 0.0001];
    let test_dec = vec![false, false, false, true, true, true, true];
    let test_final_string = vec!["100", "10", "1", "0.1", "0.01", "0.001", "0.0001"];

    for i in 0..f100.len() {
        let value = f100[i];
        println!("{}", value);
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            rhs_string_len: x.rhs_string_len(x.final_string()),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, f100[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
        println!("complete!");
    }

    //$sigfig
    //[1] 3
    //$num
    //[1] TRUE TRUE TRUE TRUE TRUE TRUE
    //$neg
    //[1] FALSE FALSE FALSE FALSE FALSE FALSE
    //$lhs
    //[1] "100" "10"  "1"   "0"   "0"   "0"
    //$lhs_zero
    //[1] FALSE FALSE FALSE  TRUE  TRUE  TRUE
    //$rhs
    //[1] 0.000 0.000 0.000 0.100 0.010 0.001
    //$rhs_digits
    //[1] 0 0 0 1 2 3
    //$dec
    //[1] FALSE FALSE FALSE  TRUE  TRUE  TRUE
    //$exp
    //[1] NA NA NA NA NA NA
    //$si
    //[1] FALSE
    //attr(,"width")
    //[1] 7
    //100
    // 10
    //  1
    //  0.1
    //  0.01
    //  0.001
}

#[test]
fn test_fn100() {
    let f100 = vec![-100.0, -10.0, -1.0, -0.1, -0.01, -0.001, -0.0001];
    let test_sigfig = vec![3, 3, 3, 3, 3, 3, 3];
    let test_neg = vec![true, true, true, true, true, true, true];
    let test_lhs = vec![100.0, 10.0, 1.0, 0.0, 0.0, 0.0, 0.0];
    let test_rhs = vec![0.0, 0.0, 0.0, 0.1, 0.01, 0.001, 0.0001];
    let test_dec = vec![false, false, false, true, true, true, true];
    let test_final_string = vec!["-100", "-10", "-1", "-0.1", "-0.01", "-0.001", "-0.0001"];

    for i in 0..f100.len() {
        let value = f100[i];
        println!("{}", value);
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            rhs_string_len: x.rhs_string_len(x.final_string()),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, f100[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
        println!("complete!");
    }
    //$sigfig
    //[1] 3
    //$num
    //[1] TRUE TRUE TRUE TRUE TRUE TRUE TRUE
    //$neg
    //[1] TRUE TRUE TRUE TRUE TRUE TRUE TRUE
    //$lhs
    //[1] "100" "10"  "1"   "0"   "0"   "0"   "0"
    //$lhs_zero
    //[1] FALSE FALSE FALSE  TRUE  TRUE  TRUE  TRUE
    //$rhs
    //[1] 0e+00 0e+00 0e+00 1e-01 1e-02 1e-03 1e-04
    //$rhs_digits
    //[1] 0 0 0 1 2 3 4
    //$dec
    //[1] FALSE FALSE FALSE  TRUE  TRUE  TRUE  TRUE
    //$exp
    //[1] NA NA NA NA NA NA NA
    //$si
    //[1] FALSE
    //attr(,"width")
    //[1] 9
}

#[test]
fn test_fn12345() {
    let f12345 = vec![-12345.0, -1234.50, -123.45, -12.345, -1.2345, -0.12345];
    let test_sigfig = vec![3, 3, 3, 3, 3, 3];
    let test_neg = vec![true, true, true, true, true, true, true];
    let test_lhs = vec![12345.0, 1234.0, 123.0, 12.0, 1.0, 0.0];
    let test_rhs = vec![
        0.0,
        0.5,
        0.45000000000000284,
        0.34500000000000064,
        0.23449999999999993,
        0.12345,
    ];
    let test_dec = vec![false, true, true, true, true, true];
    let test_final_string = vec!["-12345", "-1234.", "-123.", "-12.3", "-1.23", "-0.123"];

    for i in 0..f12345.len() {
        let value = f12345[i];
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            rhs_string_len: x.rhs_string_len(x.final_string()),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, f12345[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
    }

    //    $sigfig
    //    [1] 3
    //    $num
    //    [1] TRUE TRUE TRUE TRUE TRUE TRUE
    //    $neg
    //    [1] FALSE FALSE FALSE FALSE FALSE FALSE
    //    $lhs
    //    [1] "12345" "1234"  "123"   "12"    "1"     "0"
    //    $lhs_zero
    //    [1] FALSE FALSE FALSE FALSE FALSE  TRUE
    //    $rhs
    //    [1] 0.000 0.000 0.000 0.300 0.230 0.123
    //    $rhs_digits
    //    [1]  0 -1  0  1  2  3
    //    $dec
    //    [1] FALSE  TRUE  TRUE  TRUE  TRUE  TRUE
    //    $exp
    //    [1] NA NA NA NA NA NA
    //    $si
    //    [1] FALSE
    //    attr(,"width")
    //    [1] 9
    //    12345
    //     1234.
    //      123.
    //       12.3
    //        1.23
    //        0.123
}

#[test]
fn test_long_double() {
    // the `rhs` break on this test. This is intentional
    // This problem led to the creation of `rhs_string_len` which counts
    // length after the final string has been generated.
    let long_double = vec![-3.33333333, -1.11111111, 3.33333333, 1.11111111];
    let test_sigfig = vec![3, 3, 3, 3];
    let test_neg = vec![true, true, false, false];
    let test_lhs = vec![3.0, 1.0, 3.0, 1.0];
    let _test_rhs = vec![0.33333333, 0.11111111, 0.33333333, 0.11111111];
    let test_dec = vec![true, true, true, true];
    let test_final_string = vec!["-3.33", "-1.11", "3.33", "1.11"];

    for i in 0..long_double.len() {
        let value = long_double[i];
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            rhs_string_len: x.rhs_string_len(x.final_string()),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, long_double[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        //assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
    }
}

#[test]
fn test_bug75() {
    // the `rhs` break on this test. This is intentional
    // This problem led to the creation of `rhs_string_len` which counts
    // length after the final string has been generated.
    let long_double = vec![-1.1];
    let test_sigfig = vec![3];
    let test_neg = vec![true];
    let test_lhs = vec![1.0];
    let _test_rhs = vec![0.1];
    let test_dec = vec![true];
    let test_final_string = vec!["-1.1"];

    for i in 0..long_double.len() {
        let value = long_double[i];
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            rhs_string_len: x.rhs_string_len(x.final_string()),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, long_double[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        //assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
    }
}
