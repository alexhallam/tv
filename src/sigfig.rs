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
//  lhs_zero: bool, - Should 0 on left hand side be included
//  rhs: f64, - Right-hand-side budget after spending the lhs digits
//  rhs_digits: i64, - number of digits on rhs
//  dec: bool, - should the decimal be included in the print
//  width: u64, - total width needed to print the final sigfig float
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

struct DecimalSplits {
    val: f64,
    sigfig: i64,
}

impl DecimalSplits {
    fn value(&self) -> f64 {
        self.val
    }
    fn sig_fig(&self) -> i64 {
        self.sigfig
    }
    fn neg(&self) -> bool {
        is_neg(self.val)
    }
    fn lhs_string(&self) -> String {
        get_lhs_string(self.val)
    }
    fn lhs_zero(&self) -> bool {
        is_lhs_zero(self.val)
    }
    fn lhs(&self) -> f64 {
        get_lhs(self.val)
    }
    fn rhs(&self) -> f64 {
        get_rhs(self.val, self.sigfig)
    }
    fn lhs_digits(&self) -> i64 {
        get_lhs_digits(self.val)
    }
    fn rhs_digits(&self) -> i64 {
        get_rhs_digits(self.val, self.sigfig)
    }
    fn dec(&self) -> bool {
        is_decimal(self.val)
    }
}

#[derive(Debug)]
struct DecimalSplitsList {
    val: f64,
    sigfig: i64,
    neg: bool,
    lhs_string: String,
    lhs_zero: bool,
    lhs: f64,
    rhs: f64,
    lhs_digits: i64,
    rhs_digits: i64,
    dec: bool,
    width: u64,
    final_string: String,
}

fn is_neg(x: f64) -> bool {
    let r: bool = x < 0.0;
    r
}
fn get_lhs(x: f64) -> f64 {
    let r: f64 = x.trunc();
    r
}
fn get_lhs_string(x: f64) -> String {
    let r: i64 = x.trunc() as i64;
    let rs: String = r.to_string();
    rs
}
fn is_lhs_zero(x: f64) -> bool {
    let r: f64 = x.log10() as f64;
    if r < 0.0 {
        true
    } else {
        false
    }
}
fn is_decimal(x: f64) -> bool {
    let r: f64 = x.trunc() as f64;
    let l = x / r;
    l > 1.0
}
fn get_rhs_digits(x: f64, sigfig: i64) -> i64 {
    let lhs = if x >= 1.0 {
        let r: i64 = x.log10().floor().abs() as i64 + 1;
        r
    } else {
        0
    };

    let r: i64 = x.log10().floor().abs() as i64 + 1; //x = 1 r = 1, x = .1 r = 2 x = .01 r = 3
    if r > sigfig && lhs < sigfig {
        r
    } else {
        sigfig - lhs
    }
}
fn get_lhs_digits(x: f64) -> i64 {
    if x >= 1.0 {
        let r: i64 = x.log10().floor().abs() as i64 + 1;
        r
    } else {
        0
    }
}
fn get_rhs(x: f64, sigfig: i64) -> f64 {
    let r = x.log10().floor().abs() as usize;
    let xint = x.trunc();
    let frac = x - xint;
    frac
    //    if x > 1.0 {
    //        frac * 10f64.powf(10.0)
    //    } else {
    //        frac
    //    }
}
fn get_width(lhs: String, dec: bool, rhs_digits: i64, sigfig: i64) -> u64 {
    let lhs_count = lhs.chars().count() as i64;
    let dec = dec as i64;
    if lhs_count > sigfig {
        let r = lhs_count + dec + rhs_digits;
        r as u64
    } else {
        sigfig as u64
    }
}
fn get_final_string(x: f64, lhs: f64, rhs: f64, neg: bool, sigfig: i64) -> String {
    if lhs == 0.0 {
        //n = ((floor(log10(abs(x))) + 1 - sigfig)
        //r =(10^n) * round(x / (10^n))
        let n = x.abs().log10().floor() + 1.0 - sigfig as f64;
        let r: f64 = 10f64.powf(n) * (x / 10f64.powf(n)).round();
        r.to_string()
    } else {
        if lhs.log10() + 1.0 >= sigfig as f64 {
            if rhs > 0.0 {
                if neg == true {
                    //concatonate:
                    //(-)
                    //(lhs)
                    //(point)
                    //(-123.45 -> -123.)
                    let total = lhs + rhs;
                    let total_string = total.to_string();
                    let total_clone = total_string.clone();
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take = vec[0].len() + 1; // lhs + point
                    let r = total_string[..len_to_take].to_string();
                    r
                } else {
                    //concatonate:
                    //(lhs)
                    //(point)
                    //(123.45 -> 123.)
                    //(123.45 -> 123.)
                    let total = lhs + rhs;
                    let total_string = total.to_string();
                    let total_clone = total_string.clone();
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take = vec[0].len() + 1; // lhs + point
                    let r = total_string[..len_to_take].to_string();
                    r
                }
            } else {
                if neg == true {
                    //concatonate:
                    //(-)
                    //(lhs)
                    //(-1234.0 -> -1234)
                    let total = lhs + rhs;
                    let total_string = total.to_string();
                    let total_clone = total_string.clone();
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take = vec[0].len(); // lhs
                    let r = total_string[..len_to_take].to_string();
                    r
                } else {
                    //concatonate:
                    //(lhs)
                    //(1234.0 -> 1234)
                    //(100.0 -> 100)
                    //let total = lhs + rhs;
                    let total = lhs;
                    //let total_string = total.to_string();
                    let total_string = x.to_string();
                    let total_clone = total_string.clone();
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take = vec[0].len(); // lhs

                    let r = total_string[..len_to_take].to_string();
                    r
                }
            }
        } else {
            if neg == true {
                //concatonate:
                //(-)
                //(lhs)
                //(point)
                //+ sigfig - log10(lhs) from rhs
                //(-12.345 -> -12.3)
                let total = lhs + rhs;
                let total_string = total.to_string();
                let total_clone = total_string.clone();
                let split = total_clone.split(".");
                let vec: Vec<&str> = split.collect();
                let len_to_take_lhs = vec[0].len(); // negative + point -> +2 to sigfig
                let len_to_take_rhs = (sigfig as f64 - lhs.log10()) as usize;
                let len_to_take = len_to_take_lhs + len_to_take_rhs;
                let r = total_string[..len_to_take].to_string();
                r
            } else {
                if rhs == 0.0 {
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
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take_lhs = vec[0].len(); // point -> +1 to sigfig
                    let r = total_string[..len_to_take_lhs].to_string();
                    r
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
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take_lhs = vec[0].len(); // point -> +1 to sigfig
                    let len_to_take_rhs = ((sigfig + 1) as usize) - len_to_take_lhs;
                    let len_to_take = len_to_take_lhs + len_to_take_rhs;
                    let r = total_string[..len_to_take].to_string();
                    r
                }
            }
        }
    }
}

fn main() {
    let f12345 = vec![12345.0, 1234.5, 123.45, 12.345, 1.2345, 0.12345];

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
            lhs_string: x.lhs_string(),
            lhs_zero: x.lhs_zero(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            lhs_digits: x.lhs_digits(),
            rhs_digits: x.rhs_digits(),
            dec: x.dec(),
            width: get_width(x.lhs_string(), x.dec(), x.rhs_digits(), x.sig_fig()),
            final_string: get_final_string(x.value(), x.lhs(), x.rhs(), x.neg(), x.sig_fig()),
        };
        println!("{:#?}", list)
    }
}

#[test]
fn test_f12345() {
    let f12345 = vec![12345.0, 1234.50, 123.45, 12.345, 1.2345, 0.12345];
    let test_sigfig = vec![3, 3, 3, 3, 3, 3];
    let test_neg = vec![false, false, false, false, false, false];
    let test_lhs_string = vec![
        "12345".to_string(),
        "1234".to_string(),
        "123".to_string(),
        "12".to_string(),
        "1".to_string(),
        "0".to_string(),
    ];
    let test_lhs_zero = vec![false, false, false, false, false, true];
    let test_lhs = vec![12345.0, 1234.0, 123.0, 12.0, 1.0, 0.0];
    let test_rhs = vec![
        0.0,
        0.5,
        0.45000000000000284,
        0.34500000000000064,
        0.23449999999999993,
        0.12345,
    ];
    let test_lhs_digits = vec![5, 4, 3, 2, 1, 0];
    let test_rhs_digits = vec![-2, -1, 0, 1, 2, 3];
    let test_dec = vec![false, true, true, true, true, true];
    let test_width = vec![3, 4, 3, 3, 3, 3];
    let test_final_string = vec!["12345", "1234.", "123.", "12.3", "1.23", "0.123"];

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
            lhs_string: x.lhs_string(),
            lhs_zero: x.lhs_zero(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            lhs_digits: x.lhs_digits(),
            rhs_digits: x.rhs_digits(),
            dec: x.dec(),
            width: get_width(x.lhs_string(), x.dec(), x.rhs_digits(), x.sig_fig()),
            final_string: get_final_string(x.value(), x.lhs(), x.rhs(), x.neg(), x.sig_fig()),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, f12345[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs_string, test_lhs_string[i]);
        assert_eq!(list.lhs_zero, test_lhs_zero[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.lhs_digits, test_lhs_digits[i]);
        assert_eq!(list.rhs_digits, test_rhs_digits[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.width, test_width[i]);
        assert_eq!(list.final_string, test_final_string[i]);
    }

    //    $sigfig
    //    [1] 3
    //
    //    $num
    //    [1] TRUE TRUE TRUE TRUE TRUE TRUE
    //
    //    $neg
    //    [1] FALSE FALSE FALSE FALSE FALSE FALSE
    //
    //    $lhs
    //    [1] "12345" "1234"  "123"   "12"    "1"     "0"
    //
    //    $lhs_zero
    //    [1] FALSE FALSE FALSE FALSE FALSE  TRUE
    //
    //    $rhs
    //    [1] 0.000 0.000 0.000 0.300 0.230 0.123
    //
    //    $rhs_digits
    //    [1]  0 -1  0  1  2  3
    //
    //    $dec
    //    [1] FALSE  TRUE  TRUE  TRUE  TRUE  TRUE
    //
    //    $exp
    //    [1] NA NA NA NA NA NA
    //
    //    $si
    //    [1] FALSE
    //
    //    attr(,"width")
    //    [1] 9
    //
    //    12345
    //     1234.
    //      123.
    //       12.3
    //        1.23
    //        0.123
}

#[test]
fn test_f100() {
    let f100 = vec![100.0, 10.0, 1.0, 0.1, 0.01, 0.001];
    let test_sigfig = vec![3, 3, 3, 3, 3, 3];
    let test_neg = vec![false, false, false, false, false, false];
    let test_lhs_string = vec![
        "100".to_string(),
        "10".to_string(),
        "1".to_string(),
        "0".to_string(),
        "0".to_string(),
        "0".to_string(),
    ];
    let test_lhs_zero = vec![false, false, false, true, true, true, true];
    let test_lhs = vec![100.0, 10.0, 1.0, 0.0, 0.0, 0.0, 0.0];
    let test_rhs = vec![0.0, 0.0, 0.0, 0.1, 0.01, 0.001, 0.0001];
    let test_lhs_digits = vec![3, 2, 1, 0, 0, 0, 0];
    let test_rhs_digits = vec![0, 0, 0, 1, 2, 3, 4];
    let test_dec = vec![false, false, false, true, true, true, true];
    let test_width = vec![3, 4, 3, 3, 3, 3];
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
            lhs_string: x.lhs_string(),
            lhs_zero: x.lhs_zero(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            lhs_digits: x.lhs_digits(),
            rhs_digits: x.rhs_digits(),
            dec: x.dec(),
            width: get_width(x.lhs_string(), x.dec(), x.rhs_digits(), x.sig_fig()),
            final_string: get_final_string(x.value(), x.lhs(), x.rhs(), x.neg(), x.sig_fig()),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, f100[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs_string, test_lhs_string[i]);
        assert_eq!(list.lhs_zero, test_lhs_zero[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.lhs_digits, test_lhs_digits[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
        println!("complete!");
    }

    //$sigfig
    //[1] 3
    //
    //$num
    //[1] TRUE TRUE TRUE TRUE TRUE TRUE
    //
    //$neg
    //[1] FALSE FALSE FALSE FALSE FALSE FALSE
    //
    //$lhs
    //[1] "100" "10"  "1"   "0"   "0"   "0"
    //
    //$lhs_zero
    //[1] FALSE FALSE FALSE  TRUE  TRUE  TRUE
    //
    //$rhs
    //[1] 0.000 0.000 0.000 0.100 0.010 0.001
    //
    //$rhs_digits
    //[1] 0 0 0 1 2 3
    //
    //$dec
    //[1] FALSE FALSE FALSE  TRUE  TRUE  TRUE
    //
    //$exp
    //[1] NA NA NA NA NA NA
    //
    //$si
    //[1] FALSE
    //
    //attr(,"width")
    //[1] 7
    //
    //100
    // 10
    //  1
    //  0.1
    //  0.01
    //  0.001
}
