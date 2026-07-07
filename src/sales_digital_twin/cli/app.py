"""CLI 入口：交互式演示系统，也支持命令行参数直接运行。"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from sales_digital_twin.core.exceptions import EmptyInputError, SalesDigitalTwinError
from sales_digital_twin.core.factory import create_pipeline
from sales_digital_twin.core.paths import examples_dir, outputs_dir
from sales_digital_twin.infrastructure.config import Settings
from sales_digital_twin.infrastructure.logging import setup_logging
from sales_digital_twin.models.input import ProcessRequest

logger = logging.getLogger(__name__)

DEMO_SAMPLES: tuple[tuple[str, str], ...] = (
    ("示例1 - 正常销售通话", "sample1_sales.txt"),
    ("示例2 - 价格谈判", "sample2_negotiation.txt"),
    ("示例3 - 非销售场景", "sample3_chitchat.txt"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sales-twin",
        description="销售数字分身 —— 从通话文本自动生成跟进记录与 CRM 建议",
    )
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument("--text", "-t", type=str, help="直接传入通话文本")
    input_group.add_argument("--file", "-f", type=Path, help="从文件读取通话文本")
    input_group.add_argument(
        "--interactive", "-i", action="store_true", help="交互式输入（输入空行结束）"
    )
    input_group.add_argument(
        "--demo",
        action="store_true",
        help="批量运行 examples/ 下三组演示样本",
    )
    parser.add_argument("--output", "-o", type=Path, help="将结果写入指定文件")
    return parser


def read_multiline_input(prompt: str = "请输入通话文本（单独一行空行结束）：") -> str:
    """从 stdin 读取多行文本，遇到空行且已有内容时结束。"""
    print(prompt)
    lines: list[str] = []
    for line in sys.stdin:
        if line.strip() == "" and lines:
            break
        lines.append(line.rstrip("\n"))
    return "\n".join(lines).strip()


def read_input(args: argparse.Namespace) -> str:
    """统一将 --text / --file / --interactive 转为字符串。"""
    if args.text:
        return args.text.strip()
    if args.file:
        path = args.file
        if not path.exists():
            raise SalesDigitalTwinError(f"文件不存在: {path}")
        return path.read_text(encoding="utf-8").strip()
    if args.interactive:
        return read_multiline_input()
    raise SalesDigitalTwinError("未指定输入方式")


def write_output(content: str, output_path: Path | None, *, auto_save: bool = True) -> None:
    """打印到 stdout；指定 --output 时写入文件，否则可选自动落盘到 outputs/。"""
    print(content)
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"\n[已保存至 {output_path}]", file=sys.stderr)
    elif auto_save:
        default_dir = outputs_dir()
        default_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        auto_path = default_dir / f"result_{timestamp}.txt"
        auto_path.write_text(content, encoding="utf-8")
        print(f"\n[已自动保存至 {auto_path}]", file=sys.stderr)


def load_sample_text(filename: str) -> str:
    path = examples_dir() / filename
    if not path.exists():
        raise SalesDigitalTwinError(f"示例文件不存在: {path}")
    return path.read_text(encoding="utf-8").strip()


def process_and_show(text: str, output_path: Path | None = None) -> None:
    """执行 Pipeline 并输出结果。"""
    if not text:
        raise EmptyInputError("输入文本不能为空")
    pipeline = create_pipeline()
    result = pipeline.process(ProcessRequest(text=text))
    write_output(result.render(), output_path)


def run_demo_batch(output_path: Path | None = None) -> int:
    """批量跑三组标准示例，用于答辩/验收演示。"""
    pipeline = create_pipeline()
    for title, filename in DEMO_SAMPLES:
        text = load_sample_text(filename)
        print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")
        result = pipeline.process(ProcessRequest(text=text))
        write_output(result.render(), output_path)
    return 0


def _print_main_menu() -> None:
    print("\n" + "=" * 60)
    print("  销售数字分身 —— 交互式演示系统")
    print("=" * 60)
    print("  1. 运行全部系统默认示例")
    print("  2. 选择单个系统默认示例")
    print("  3. 自定义输入通话文本")
    print("  0. 退出")
    print("-" * 60)


def _print_sample_menu() -> None:
    print("\n请选择系统默认示例：")
    for index, (title, _) in enumerate(DEMO_SAMPLES, start=1):
        print(f"  {index}. {title}")
    print("  0. 返回上级菜单")


def _run_single_demo() -> None:
    _print_sample_menu()
    choice = input("请输入编号: ").strip()
    if choice == "0":
        return
    if not choice.isdigit():
        print("无效输入，请输入数字编号。", file=sys.stderr)
        return
    index = int(choice) - 1
    if index < 0 or index >= len(DEMO_SAMPLES):
        print("编号超出范围，请重新选择。", file=sys.stderr)
        return

    title, filename = DEMO_SAMPLES[index]
    text = load_sample_text(filename)
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")
    process_and_show(text)


def run_interactive_demo() -> int:
    """交互式演示：用户选择系统默认示例或自定义输入。"""
    print("欢迎使用销售数字分身演示系统。")

    while True:
        _print_main_menu()
        choice = input("请选择: ").strip()

        try:
            if choice == "0":
                print("感谢使用，再见！")
                return 0
            if choice == "1":
                run_demo_batch()
            elif choice == "2":
                _run_single_demo()
            elif choice == "3":
                text = read_multiline_input()
                if not text:
                    raise EmptyInputError("未输入通话文本")
                print(f"\n{'=' * 60}\n自定义输入\n{'=' * 60}")
                process_and_show(text)
            else:
                print("无效选择，请输入 0-3。", file=sys.stderr)
                continue
        except EmptyInputError as exc:
            logger.error("%s", exc)
            print(f"错误: {exc}", file=sys.stderr)
        except SalesDigitalTwinError as exc:
            logger.error("%s", exc)
            print(f"错误: {exc}", file=sys.stderr)

        if input("\n按 Enter 继续，或输入 q 退出: ").strip().lower() == "q":
            print("感谢使用，再见！")
            return 0


def _has_cli_input(args: argparse.Namespace) -> bool:
    return bool(args.text or args.file or args.interactive or args.demo)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    settings = Settings()
    setup_logging(settings.log_level)

    try:
        if not _has_cli_input(args):
            return run_interactive_demo()

        if args.demo:
            return run_demo_batch(args.output)

        text = read_input(args)
        if not text:
            raise EmptyInputError("输入文本不能为空")

        process_and_show(text, args.output)
        return 0
    except EmptyInputError as exc:
        logger.error("%s", exc)
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    except SalesDigitalTwinError as exc:
        logger.error("%s", exc)
        print(f"错误: {exc}", file=sys.stderr)
        return 1
